import json
import os
import secrets
import urllib.error
import urllib.parse
import urllib.request
from typing import List
from asgiref.sync import sync_to_async
from django.contrib.auth import get_user_model
from django.db.models import Count, Q, Sum
from django.utils.text import slugify
from ninja import Router
from ninja.errors import HttpError
from store.models import Order, Product, ProductVariant
from .auth_helpers import (
    AsyncAdminAuthBearer,
    AsyncAuthBearer,
    create_notification,
    create_token,
    decode_token,
    record_audit,
    require_permission,
)
from .models import ALL_PERMISSIONS, AuditLog, CustomerAddress, Notification, StaffRole
from .schemas import (
    AddressOutSchema,
    AddressWriteSchema,
    AuditLogOutSchema,
    ChangePasswordSchema,
    CollaboratorCreateSchema,
    CollaboratorUpdateSchema,
    CustomerSummarySchema,
    GoogleAuthSchema,
    LoginSchema,
    NotificationListOutSchema,
    RegisterSchema,
    RoleOutSchema,
    RoleWriteSchema,
    TokenResponseSchema,
    TwoFactorCodeSchema,
    TwoFactorDisableSchema,
    TwoFactorVerifyLoginSchema,
    UpdateProfileSchema,
    UserOutSchema,
)
from .totp import (
    build_otpauth_uri,
    generate_backup_codes,
    generate_totp_secret,
    verify_totp_code,
)

User = get_user_model()
router = Router(tags=["Authentification, RBAC, 2FA & Équipe ESTLE"])


def _serialize_user(user) -> dict:
    role = getattr(user, "role", None)
    return {
        "id": user.id,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "phone_number": user.phone_number,
        "default_city": user.default_city,
        "default_commune": user.default_commune,
        "default_address": user.default_address,
        "account_type": user.account_type,
        "role_id": role.id if role else None,
        "role_code": role.code if role else None,
        "role_name": role.name if role else ("Super Admin" if user.is_superuser else "Client"),
        "permissions": user.effective_permissions,
        "extra_permissions": user.extra_permissions or [],
        "job_title": user.job_title or "",
        "is_2fa_enabled": user.is_2fa_enabled,
        "is_staff": user.is_staff,
        "is_superuser": user.is_superuser,
        "is_active": user.is_active,
        "date_joined": user.date_joined,
    }


async def _get_or_create_client_role() -> StaffRole:
    role, _ = await StaffRole.objects.aget_or_create(
        code="client",
        defaults={
            "name": "Client",
            "description": "Rôle attribué automatiquement à tout client inscrit sur la boutique.",
            "permissions": [],
            "is_system": True,
        },
    )
    return role


# ============================================================================
# 1. AUTHENTIFICATION CLIENT / COLLABORATEUR + GOOGLE + 2FA
# ============================================================================

@router.post("/register", response={201: TokenResponseSchema})
async def register(request, data: RegisterSchema):
    exists = await User.objects.filter(email=data.email.lower()).aexists()
    if exists:
        raise HttpError(400, "Un compte avec cette adresse e-mail existe déjà.")

    client_role = await _get_or_create_client_role()

    user = await sync_to_async(User.objects.create_user)(
        email=data.email.lower(),
        password=data.password,
        first_name=data.first_name,
        last_name=data.last_name,
        phone_number=data.phone_number,
        default_city=data.default_city,
        default_commune=data.default_commune,
        default_address=data.default_address,
        account_type="CLIENT",
        role=client_role,
        is_staff=False,
    )
    user = await User.objects.select_related("role").aget(id=user.id)

    access_token = create_token(user.id, token_type="access")
    refresh_token = create_token(user.id, token_type="refresh")

    return 201, {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "Bearer",
        "requires_2fa": False,
        "temp_token": "",
        "user": _serialize_user(user),
    }


@router.post("/login", response=TokenResponseSchema)
async def login(request, data: LoginSchema):
    try:
        user = await User.objects.select_related("role").aget(email=data.email.lower())
    except User.DoesNotExist:
        raise HttpError(401, "Identifiants invalides.")

    valid = await sync_to_async(user.check_password)(data.password)
    if not valid:
        raise HttpError(401, "Identifiants invalides.")

    if not user.is_active:
        raise HttpError(403, "Ce compte a été désactivé.")

    if user.is_2fa_enabled and user.totp_secret:
        temp_token = create_token(user.id, token_type="2fa_temp")
        return {
            "access_token": "",
            "refresh_token": "",
            "token_type": "Bearer",
            "requires_2fa": True,
            "temp_token": temp_token,
            "user": _serialize_user(user),
        }

    access_token = create_token(user.id, token_type="access")
    refresh_token = create_token(user.id, token_type="refresh")

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "Bearer",
        "requires_2fa": False,
        "temp_token": "",
        "user": _serialize_user(user),
    }


@router.post("/2fa/verify", response=TokenResponseSchema)
async def verify_2fa_login(request, data: TwoFactorVerifyLoginSchema):
    payload = decode_token(data.temp_token)
    if not payload or payload.get("token_type") != "2fa_temp":
        raise HttpError(401, "Session 2FA expirée. Veuillez vous reconnecter.")

    try:
        user = await User.objects.select_related("role").aget(
            id=payload.get("user_id"), is_active=True
        )
    except User.DoesNotExist:
        raise HttpError(401, "Utilisateur introuvable.")

    raw_code = data.code.strip().upper()
    is_valid_totp = verify_totp_code(user.totp_secret, raw_code)
    is_valid_backup = False

    if not is_valid_totp and isinstance(user.backup_codes, list):
        if raw_code in user.backup_codes:
            is_valid_backup = True
            remaining = [c for c in user.backup_codes if c != raw_code]
            user.backup_codes = remaining
            await user.asave(update_fields=["backup_codes"])

    if not is_valid_totp and not is_valid_backup:
        raise HttpError(401, "Code 2FA ou code de secours invalide.")

    access_token = create_token(user.id, token_type="access")
    refresh_token = create_token(user.id, token_type="refresh")

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "Bearer",
        "requires_2fa": False,
        "temp_token": "",
        "user": _serialize_user(user),
    }


def _verify_google_credential(credential: str) -> dict:
    token = (credential or "").strip()
    if not token:
        raise HttpError(401, "Jeton Google manquant.")

    expected_aud = os.environ.get("GOOGLE_CLIENT_ID", "").strip()
    is_jwt = token.count(".") == 2

    if is_jwt:
        url = f"https://oauth2.googleapis.com/tokeninfo?{urllib.parse.urlencode({'id_token': token})}"
        req = urllib.request.Request(url, headers={"Accept": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=8) as resp:
                payload = json.loads(resp.read().decode("utf-8"))
        except (urllib.error.URLError, urllib.error.HTTPError, ValueError):
            raise HttpError(401, "Jeton Google invalide ou expiré.")

        if expected_aud and payload.get("aud") != expected_aud:
            raise HttpError(401, "Client ID Google non autorisé.")

        email = (payload.get("email") or "").strip().lower()
        if not email or str(payload.get("email_verified", "")).lower() not in ("true", "1"):
            raise HttpError(401, "Adresse e-mail Google non vérifiée.")

        return {
            "email": email,
            "first_name": (payload.get("given_name") or "").strip(),
            "last_name": (payload.get("family_name") or "").strip(),
        }

    # OAuth2 Access Token (fenêtre popup Google Account Chooser)
    if expected_aud:
        info_url = f"https://oauth2.googleapis.com/tokeninfo?{urllib.parse.urlencode({'access_token': token})}"
        info_req = urllib.request.Request(info_url, headers={"Accept": "application/json"})
        try:
            with urllib.request.urlopen(info_req, timeout=8) as resp:
                token_info = json.loads(resp.read().decode("utf-8"))
        except (urllib.error.URLError, urllib.error.HTTPError, ValueError):
            raise HttpError(401, "Jeton d'accès Google invalide ou expiré.")
        if token_info.get("aud") != expected_aud and token_info.get("azp") != expected_aud:
            raise HttpError(401, "Client ID Google non autorisé.")

    userinfo_req = urllib.request.Request(
        "https://www.googleapis.com/oauth2/v3/userinfo",
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(userinfo_req, timeout=8) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
    except (urllib.error.URLError, urllib.error.HTTPError, ValueError):
        raise HttpError(401, "Impossible de récupérer le profil Google.")

    email = (payload.get("email") or "").strip().lower()
    if not email or str(payload.get("email_verified", "")).lower() not in ("true", "1"):
        raise HttpError(401, "Adresse e-mail Google non vérifiée.")

    return {
        "email": email,
        "first_name": (payload.get("given_name") or "").strip(),
        "last_name": (payload.get("family_name") or "").strip(),
    }


@router.post("/google", response=TokenResponseSchema)
async def google_auth(request, data: GoogleAuthSchema):
    profile = await sync_to_async(_verify_google_credential)(data.credential)

    try:
        user = await User.objects.select_related("role").aget(email=profile["email"])
    except User.DoesNotExist:
        client_role = await _get_or_create_client_role()
        user = await sync_to_async(User.objects.create_user)(
            email=profile["email"],
            password=secrets.token_urlsafe(32),
            first_name=profile["first_name"],
            last_name=profile["last_name"],
            phone_number="",
            default_city="Abidjan",
            default_commune="Cocody",
            account_type="CLIENT",
            role=client_role,
            is_staff=False,
        )
        user = await User.objects.select_related("role").aget(id=user.id)

    if not user.is_active:
        raise HttpError(403, "Ce compte a été désactivé.")

    if user.is_2fa_enabled and user.totp_secret:
        temp_token = create_token(user.id, token_type="2fa_temp")
        return {
            "access_token": "",
            "refresh_token": "",
            "token_type": "Bearer",
            "requires_2fa": True,
            "temp_token": temp_token,
            "user": _serialize_user(user),
        }

    access_token = create_token(user.id, token_type="access")
    refresh_token = create_token(user.id, token_type="refresh")

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "Bearer",
        "requires_2fa": False,
        "temp_token": "",
        "user": _serialize_user(user),
    }


# ============================================================================
# 2. PROFIL UTILISATEUR, MOT DE PASSE & CONFIGURATION 2FA
# ============================================================================

@router.get("/me", response=UserOutSchema, auth=AsyncAuthBearer())
async def get_me(request):
    return _serialize_user(request.auth)


@router.put("/me", response=UserOutSchema, auth=AsyncAuthBearer())
async def update_me(request, data: UpdateProfileSchema):
    user = request.auth
    user.first_name = data.first_name
    user.last_name = data.last_name
    user.phone_number = data.phone_number
    user.default_city = data.default_city
    user.default_commune = data.default_commune
    user.default_address = data.default_address
    if data.job_title is not None and (user.account_type == "COLLABORATOR" or user.is_staff):
        user.job_title = data.job_title
    await user.asave()
    return _serialize_user(user)


@router.post("/change-password", auth=AsyncAuthBearer())
async def change_password(request, data: ChangePasswordSchema):
    user = request.auth
    ok = await sync_to_async(user.check_password)(data.current_password)
    if not ok:
        raise HttpError(400, "Le mot de passe actuel est incorrect.")
    await sync_to_async(user.set_password)(data.new_password)
    await user.asave()
    await record_audit(user, "PASSWORD_CHANGED", f"Mot de passe modifié par {user.email}", "User", str(user.id))
    return {"success": True, "message": "Mot de passe mis à jour avec succès."}


@router.post("/2fa/setup", auth=AsyncAuthBearer())
async def setup_2fa(request):
    user = request.auth
    secret = generate_totp_secret()
    user.totp_secret = secret
    await user.asave(update_fields=["totp_secret"])
    otpauth_uri = build_otpauth_uri(user.email, secret, issuer="ESTLE")
    qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=220x220&data={urllib.parse.quote(otpauth_uri)}"
    return {
        "secret": secret,
        "otpauth_uri": otpauth_uri,
        "qr_url": qr_url,
    }


@router.post("/2fa/enable", auth=AsyncAuthBearer())
async def enable_2fa(request, data: TwoFactorCodeSchema):
    user = request.auth
    if not user.totp_secret:
        raise HttpError(400, "Veuillez d'abord initialiser la configuration 2FA.")
    if not verify_totp_code(user.totp_secret, data.code):
        raise HttpError(400, "Code à 6 chiffres invalide. Vérifiez votre application Authenticator.")

    codes = generate_backup_codes(6)
    user.is_2fa_enabled = True
    user.backup_codes = codes
    await user.asave(update_fields=["is_2fa_enabled", "backup_codes"])
    await record_audit(user, "TWO_FA_ENABLED", f"2FA activée pour {user.email}", "User", str(user.id))
    return {
        "enabled": True,
        "backup_codes": codes,
        "user": _serialize_user(user),
    }


@router.post("/2fa/disable", auth=AsyncAuthBearer())
async def disable_2fa(request, data: TwoFactorDisableSchema):
    user = request.auth
    verified = False
    if data.password:
        verified = await sync_to_async(user.check_password)(data.password)
    if not verified and data.code and user.totp_secret:
        verified = verify_totp_code(user.totp_secret, data.code)
    if not verified:
        raise HttpError(400, "Mot de passe ou code 2FA requis pour désactiver la 2FA.")

    user.is_2fa_enabled = False
    user.totp_secret = ""
    user.backup_codes = []
    await user.asave(update_fields=["is_2fa_enabled", "totp_secret", "backup_codes"])
    await record_audit(user, "TWO_FA_DISABLED", f"2FA désactivée pour {user.email}", "User", str(user.id))
    return {"enabled": False, "user": _serialize_user(user)}


# ============================================================================
# 3. CARNET D'ADRESSES CLIENT (MAX 3 ADRESSES + GPS RÉEL)
# ============================================================================

@router.get("/addresses", response=List[AddressOutSchema], auth=AsyncAuthBearer())
async def list_my_addresses(request):
    return [a async for a in CustomerAddress.objects.filter(user=request.auth).order_by("-is_default", "-created_at")]


@router.post("/addresses", response={201: AddressOutSchema}, auth=AsyncAuthBearer())
async def create_address(request, data: AddressWriteSchema):
    user = request.auth
    current_count = await CustomerAddress.objects.filter(user=user).acount()
    if current_count >= 3:
        raise HttpError(400, "Vous pouvez enregistrer au maximum 3 adresses de livraison.")

    is_default = data.is_default or current_count == 0
    if is_default:
        await CustomerAddress.objects.filter(user=user, is_default=True).aupdate(is_default=False)

    addr = await CustomerAddress.objects.acreate(
        user=user,
        label=data.label or "Maison",
        recipient_name=data.recipient_name or user.full_name,
        phone=data.phone or user.phone_number,
        delivery_zone_type=data.delivery_zone_type,
        city=data.city,
        commune=data.commune,
        address_details=data.address_details,
        landmark=data.landmark,
        latitude=data.latitude,
        longitude=data.longitude,
        is_default=is_default,
    )
    return 201, addr


@router.put("/addresses/{addr_id}", response=AddressOutSchema, auth=AsyncAuthBearer())
async def update_address(request, addr_id: int, data: AddressWriteSchema):
    user = request.auth
    try:
        addr = await CustomerAddress.objects.aget(id=addr_id, user=user)
    except CustomerAddress.DoesNotExist:
        raise HttpError(404, "Adresse introuvable.")

    if data.is_default:
        await CustomerAddress.objects.filter(user=user, is_default=True).exclude(id=addr_id).aupdate(is_default=False)

    addr.label = data.label or addr.label
    addr.recipient_name = data.recipient_name
    addr.phone = data.phone
    addr.delivery_zone_type = data.delivery_zone_type
    addr.city = data.city
    addr.commune = data.commune
    addr.address_details = data.address_details
    addr.landmark = data.landmark
    addr.latitude = data.latitude
    addr.longitude = data.longitude
    addr.is_default = data.is_default
    await addr.asave()
    return addr


@router.delete("/addresses/{addr_id}", auth=AsyncAuthBearer())
async def delete_address(request, addr_id: int):
    user = request.auth
    deleted, _ = await CustomerAddress.objects.filter(id=addr_id, user=user).adelete()
    if not deleted:
        raise HttpError(404, "Adresse introuvable.")
    remaining = await CustomerAddress.objects.filter(user=user).afirst()
    if remaining and not await CustomerAddress.objects.filter(user=user, is_default=True).aexists():
        remaining.is_default = True
        await remaining.asave(update_fields=["is_default"])
    return {"deleted": True}


@router.post("/addresses/{addr_id}/default", response=AddressOutSchema, auth=AsyncAuthBearer())
async def set_default_address(request, addr_id: int):
    user = request.auth
    try:
        addr = await CustomerAddress.objects.aget(id=addr_id, user=user)
    except CustomerAddress.DoesNotExist:
        raise HttpError(404, "Adresse introuvable.")
    await CustomerAddress.objects.filter(user=user, is_default=True).aupdate(is_default=False)
    addr.is_default = True
    await addr.asave(update_fields=["is_default"])
    return addr


# ============================================================================
# 4. ADMINISTRATION : KPIs, RÔLES & PERMISSIONS, COLLABORATEURS, CLIENTS & AUDIT
# ============================================================================

@router.get("/admin/dashboard", auth=AsyncAdminAuthBearer())
async def admin_dashboard_kpis(request):
    def _compute():
        orders_qs = Order.objects.all()
        total_orders = orders_qs.count()
        pending_orders = orders_qs.filter(status="PENDING").count()
        shipping_orders = orders_qs.filter(status="SHIPPING").count()
        delivered_orders = orders_qs.filter(status="DELIVERED").count()
        total_revenue = (
            orders_qs.exclude(status="CANCELLED").aggregate(s=Sum("total_fcfa"))["s"] or 0
        )

        total_products = Product.objects.filter(is_active=True).count()
        total_customers = User.objects.filter(account_type="CLIENT", is_staff=False).count()
        total_collaborators = User.objects.filter(account_type="COLLABORATOR").count()

        low_stock_qs = (
            ProductVariant.objects.select_related("product")
            .filter(product__is_active=True, stock__lte=3)
            .order_by("stock", "product__name")[:12]
        )
        low_stock = [
            {
                "variant_id": v.id,
                "product_id": v.product_id,
                "product_name": v.product.name,
                "size": v.size,
                "color_name": v.color_name,
                "stock": v.stock,
            }
            for v in low_stock_qs
        ]

        recent_orders = [
            {
                "id": o.id,
                "order_number": o.order_number,
                "full_name": o.full_name,
                "city": o.city,
                "commune": o.commune,
                "total_fcfa": o.total_fcfa,
                "status": o.status,
                "payment_method": o.payment_method,
                "created_at": o.created_at.isoformat(),
            }
            for o in orders_qs.order_by("-created_at")[:6]
        ]

        return {
            "total_revenue_fcfa": total_revenue,
            "total_orders": total_orders,
            "pending_orders": pending_orders,
            "shipping_orders": shipping_orders,
            "delivered_orders": delivered_orders,
            "total_products": total_products,
            "total_customers": total_customers,
            "total_collaborators": total_collaborators,
            "low_stock": low_stock,
            "recent_orders": recent_orders,
        }

    return await sync_to_async(_compute)()


@router.get("/admin/permissions", auth=AsyncAdminAuthBearer())
async def list_permissions(request):
    return ALL_PERMISSIONS


@router.get("/admin/roles", response=List[RoleOutSchema], auth=AsyncAdminAuthBearer())
async def list_roles(request):
    def _fetch():
        roles = StaffRole.objects.annotate(user_count=Count("users")).order_by("id")
        return [
            {
                "id": r.id,
                "code": r.code,
                "name": r.name,
                "description": r.description,
                "permissions": r.permissions or [],
                "is_system": r.is_system,
                "user_count": r.user_count,
            }
            for r in roles
        ]

    return await sync_to_async(_fetch)()


@router.post("/admin/roles", response={201: RoleOutSchema}, auth=AsyncAdminAuthBearer())
async def create_role(request, data: RoleWriteSchema):
    require_permission(request.auth, "roles.manage")
    code = slugify(data.code or data.name).replace("-", "_")
    if not code:
        raise HttpError(400, "Code de rôle invalide.")
    if await StaffRole.objects.filter(code=code).aexists():
        raise HttpError(400, "Un rôle avec ce code existe déjà.")

    role = await StaffRole.objects.acreate(
        code=code,
        name=data.name.strip(),
        description=data.description.strip(),
        permissions=data.permissions,
        is_system=False,
    )
    await record_audit(request.auth, "ROLE_CREATED", f"Rôle créé : {role.name}", "StaffRole", str(role.id))
    return 201, {
        "id": role.id,
        "code": role.code,
        "name": role.name,
        "description": role.description,
        "permissions": role.permissions or [],
        "is_system": role.is_system,
        "user_count": 0,
    }


@router.put("/admin/roles/{role_id}", response=RoleOutSchema, auth=AsyncAdminAuthBearer())
async def update_role(request, role_id: int, data: RoleWriteSchema):
    require_permission(request.auth, "roles.manage")
    try:
        role = await StaffRole.objects.aget(id=role_id)
    except StaffRole.DoesNotExist:
        raise HttpError(404, "Rôle introuvable.")

    role.name = data.name.strip()
    role.description = data.description.strip()
    if role.code != "super_admin":
        role.permissions = data.permissions
    await role.asave()
    user_count = await User.objects.filter(role_id=role.id).acount()
    await record_audit(request.auth, "ROLE_UPDATED", f"Rôle mis à jour : {role.name}", "StaffRole", str(role.id))
    return {
        "id": role.id,
        "code": role.code,
        "name": role.name,
        "description": role.description,
        "permissions": role.permissions or [],
        "is_system": role.is_system,
        "user_count": user_count,
    }


@router.delete("/admin/roles/{role_id}", auth=AsyncAdminAuthBearer())
async def delete_role(request, role_id: int):
    require_permission(request.auth, "roles.manage")
    try:
        role = await StaffRole.objects.aget(id=role_id)
    except StaffRole.DoesNotExist:
        raise HttpError(404, "Rôle introuvable.")
    if role.is_system:
        raise HttpError(400, "Impossible de supprimer un rôle système.")
    name = role.name
    await role.adelete()
    await record_audit(request.auth, "ROLE_DELETED", f"Rôle supprimé : {name}", "StaffRole", str(role_id))
    return {"deleted": True}


@router.get("/admin/collaborators", response=List[UserOutSchema], auth=AsyncAdminAuthBearer())
async def list_collaborators(request):
    require_permission(request.auth, "team.manage")
    users = [
        _serialize_user(u)
        async for u in User.objects.select_related("role")
        .filter(account_type="COLLABORATOR")
        .order_by("-is_superuser", "-date_joined")
    ]
    return users


@router.post("/admin/collaborators", response={201: UserOutSchema}, auth=AsyncAdminAuthBearer())
async def create_collaborator(request, data: CollaboratorCreateSchema):
    require_permission(request.auth, "team.manage")
    email = data.email.strip().lower()
    if await User.objects.filter(email=email).aexists():
        raise HttpError(400, "Un utilisateur avec cette adresse e-mail existe déjà.")

    role = None
    if data.role_id:
        try:
            role = await StaffRole.objects.aget(id=data.role_id)
        except StaffRole.DoesNotExist:
            raise HttpError(400, "Rôle sélectionné introuvable.")

    user = await sync_to_async(User.objects.create_user)(
        email=email,
        password=data.password,
        first_name=data.first_name.strip(),
        last_name=data.last_name.strip(),
        phone_number=data.phone_number.strip(),
        job_title=data.job_title.strip(),
        account_type="COLLABORATOR",
        role=role,
        extra_permissions=data.extra_permissions,
        is_staff=True,
        is_active=True,
    )
    user = await User.objects.select_related("role").aget(id=user.id)
    await record_audit(
        request.auth,
        "COLLABORATOR_CREATED",
        f"Collaborateur créé : {user.email} ({role.name if role else 'Sans rôle'})",
        "User",
        str(user.id),
    )
    return 201, _serialize_user(user)


@router.put("/admin/collaborators/{collab_id}", response=UserOutSchema, auth=AsyncAdminAuthBearer())
async def update_collaborator(request, collab_id: int, data: CollaboratorUpdateSchema):
    require_permission(request.auth, "team.manage")
    try:
        user = await User.objects.select_related("role").aget(id=collab_id, account_type="COLLABORATOR")
    except User.DoesNotExist:
        raise HttpError(404, "Collaborateur introuvable.")

    if data.first_name is not None:
        user.first_name = data.first_name.strip()
    if data.last_name is not None:
        user.last_name = data.last_name.strip()
    if data.phone_number is not None:
        user.phone_number = data.phone_number.strip()
    if data.job_title is not None:
        user.job_title = data.job_title.strip()
    if data.role_id is not None:
        try:
            user.role = await StaffRole.objects.aget(id=data.role_id)
        except StaffRole.DoesNotExist:
            raise HttpError(400, "Rôle introuvable.")
    if data.extra_permissions is not None:
        user.extra_permissions = data.extra_permissions
    if data.is_active is not None:
        if user.id == request.auth.id and not data.is_active:
            raise HttpError(400, "Vous ne pouvez pas désactiver votre propre compte.")
        user.is_active = data.is_active
    if data.new_password and len(data.new_password) >= 8:
        await sync_to_async(user.set_password)(data.new_password)

    await user.asave()
    user = await User.objects.select_related("role").aget(id=user.id)
    await record_audit(
        request.auth,
        "COLLABORATOR_UPDATED",
        f"Collaborateur mis à jour : {user.email}",
        "User",
        str(user.id),
    )
    return _serialize_user(user)


@router.post("/admin/collaborators/{collab_id}/reset-2fa", response=UserOutSchema, auth=AsyncAdminAuthBearer())
async def reset_collaborator_2fa(request, collab_id: int):
    require_permission(request.auth, "team.manage")
    try:
        user = await User.objects.select_related("role").aget(id=collab_id, account_type="COLLABORATOR")
    except User.DoesNotExist:
        raise HttpError(404, "Collaborateur introuvable.")
    user.is_2fa_enabled = False
    user.totp_secret = ""
    user.backup_codes = []
    await user.asave(update_fields=["is_2fa_enabled", "totp_secret", "backup_codes"])
    await record_audit(
        request.auth,
        "COLLABORATOR_2FA_RESET",
        f"2FA réinitialisée pour {user.email}",
        "User",
        str(user.id),
    )
    return _serialize_user(user)


@router.delete("/admin/collaborators/{collab_id}", auth=AsyncAdminAuthBearer())
async def delete_collaborator(request, collab_id: int):
    require_permission(request.auth, "team.manage")
    if collab_id == request.auth.id:
        raise HttpError(400, "Vous ne pouvez pas supprimer votre propre compte.")
    try:
        user = await User.objects.aget(id=collab_id, account_type="COLLABORATOR")
    except User.DoesNotExist:
        raise HttpError(404, "Collaborateur introuvable.")
    if user.is_superuser:
        raise HttpError(400, "Impossible de supprimer le compte Super Admin principal.")
    email = user.email
    await user.adelete()
    await record_audit(request.auth, "COLLABORATOR_DELETED", f"Collaborateur supprimé : {email}", "User", str(collab_id))
    return {"deleted": True}


@router.get("/admin/customers", response=List[CustomerSummarySchema], auth=AsyncAdminAuthBearer())
async def list_customers(request):
    require_permission(request.auth, "customers.view")

    def _fetch():
        clients = (
            User.objects.filter(account_type="CLIENT", is_staff=False)
            .prefetch_related("addresses")
            .order_by("-date_joined")
        )
        order_stats = {
            row["user_id"]: (row["cnt"], row["spent"] or 0)
            for row in Order.objects.filter(user__isnull=False)
            .exclude(status="CANCELLED")
            .values("user_id")
            .annotate(cnt=Count("id"), spent=Sum("total_fcfa"))
        }
        out = []
        for u in clients:
            cnt, spent = order_stats.get(u.id, (0, 0))
            out.append(
                {
                    "id": u.id,
                    "email": u.email,
                    "first_name": u.first_name,
                    "last_name": u.last_name,
                    "phone_number": u.phone_number,
                    "default_city": u.default_city,
                    "default_commune": u.default_commune,
                    "default_address": u.default_address,
                    "is_active": u.is_active,
                    "is_2fa_enabled": u.is_2fa_enabled,
                    "date_joined": u.date_joined,
                    "orders_count": cnt,
                    "total_spent_fcfa": spent,
                    "addresses": list(u.addresses.all()),
                }
            )
        return out

    return await sync_to_async(_fetch)()


@router.post("/admin/customers/{customer_id}/toggle-active", auth=AsyncAdminAuthBearer())
async def toggle_customer_active(request, customer_id: int):
    require_permission(request.auth, "customers.manage")
    try:
        user = await User.objects.aget(id=customer_id, account_type="CLIENT")
    except User.DoesNotExist:
        raise HttpError(404, "Client introuvable.")
    user.is_active = not user.is_active
    await user.asave(update_fields=["is_active"])
    status_label = "réactivé" if user.is_active else "suspendu"
    await record_audit(
        request.auth,
        "CUSTOMER_STATUS_CHANGED",
        f"Compte client {user.email} {status_label}",
        "User",
        str(user.id),
    )
    return {"id": user.id, "is_active": user.is_active}


# ============================================================================
# 6. NOTIFICATIONS (CLOCHE CLIENT & CLOCHE ADMIN FILTRÉE PAR PERMISSIONS RBAC)
# ============================================================================

@router.get("/notifications", response=NotificationListOutSchema, auth=AsyncAuthBearer())
async def list_client_notifications(request):
    user = request.auth
    qs = Notification.objects.filter(audience="CLIENT", recipient_id=user.id).order_by("-created_at")[:30]
    items = []
    unread = 0
    async for n in qs:
        is_read = bool(n.is_read)
        if not is_read:
            unread += 1
        items.append(
            {
                "id": n.id,
                "audience": n.audience,
                "category": n.category,
                "title": n.title,
                "message": n.message,
                "link": n.link,
                "is_read": is_read,
                "created_at": n.created_at,
            }
        )
    return {"unread_count": unread, "items": items}


@router.post("/notifications/{notif_id}/read", auth=AsyncAuthBearer())
async def mark_client_notification_read(request, notif_id: int):
    user = request.auth
    updated = await Notification.objects.filter(
        id=notif_id, audience="CLIENT", recipient_id=user.id
    ).aupdate(is_read=True)
    if not updated:
        raise HttpError(404, "Notification introuvable.")
    return {"ok": True}


@router.post("/notifications/read-all", auth=AsyncAuthBearer())
async def mark_all_client_notifications_read(request):
    user = request.auth
    await Notification.objects.filter(
        audience="CLIENT", recipient_id=user.id, is_read=False
    ).aupdate(is_read=True)
    return {"ok": True}


@router.get("/admin/notifications", response=NotificationListOutSchema, auth=AsyncAdminAuthBearer())
async def list_admin_notifications(request):
    user = request.auth
    qs = Notification.objects.filter(audience="ADMIN").filter(
        Q(recipient__isnull=True) | Q(recipient_id=user.id)
    ).order_by("-created_at")[:50]

    items = []
    unread = 0
    async for n in qs:
        # Sécurité RBAC stricte : un collaborateur sans la permission requise
        # ne voit NI la notification NI son lien de redirection
        if n.required_permission and not user.has_estle_perm(n.required_permission):
            continue
        is_read = n.is_read_for(user.id)
        if not is_read:
            unread += 1
        items.append(
            {
                "id": n.id,
                "audience": n.audience,
                "category": n.category,
                "title": n.title,
                "message": n.message,
                "link": n.link,
                "is_read": is_read,
                "created_at": n.created_at,
            }
        )
        if len(items) >= 30:
            break
    return {"unread_count": unread, "items": items}


@router.post("/admin/notifications/{notif_id}/read", auth=AsyncAdminAuthBearer())
async def mark_admin_notification_read(request, notif_id: int):
    user = request.auth
    try:
        n = await Notification.objects.aget(id=notif_id, audience="ADMIN")
    except Notification.DoesNotExist:
        raise HttpError(404, "Notification introuvable.")
    if n.recipient_id is not None and n.recipient_id != user.id:
        raise HttpError(403, "Accès refusé.")
    if n.required_permission and not user.has_estle_perm(n.required_permission):
        raise HttpError(403, "Permission insuffisante.")

    if n.recipient_id == user.id:
        n.is_read = True
        await n.asave(update_fields=["is_read"])
    else:
        ids = list(n.read_by_ids or [])
        if user.id not in ids:
            ids.append(user.id)
            n.read_by_ids = ids
            await n.asave(update_fields=["read_by_ids"])
    return {"ok": True}


@router.post("/admin/notifications/read-all", auth=AsyncAdminAuthBearer())
async def mark_all_admin_notifications_read(request):
    user = request.auth
    qs = Notification.objects.filter(audience="ADMIN").filter(
        Q(recipient__isnull=True) | Q(recipient_id=user.id)
    ).order_by("-created_at")[:50]
    async for n in qs:
        if n.required_permission and not user.has_estle_perm(n.required_permission):
            continue
        if n.recipient_id == user.id:
            if not n.is_read:
                n.is_read = True
                await n.asave(update_fields=["is_read"])
        else:
            ids = list(n.read_by_ids or [])
            if user.id not in ids:
                ids.append(user.id)
                n.read_by_ids = ids
                await n.asave(update_fields=["read_by_ids"])
    return {"ok": True}


@router.get("/admin/audit-logs", response=List[AuditLogOutSchema], auth=AsyncAdminAuthBearer())
async def list_audit_logs(request):
    require_permission(request.auth, "audit.view")
    return [
        {
            "id": log.id,
            "actor_email": log.actor_email,
            "action": log.action,
            "target_type": log.target_type,
            "target_id": log.target_id,
            "summary": log.summary,
            "metadata": log.metadata or {},
            "created_at": log.created_at,
        }
        async for log in AuditLog.objects.all().order_by("-created_at")[:100]
    ]
