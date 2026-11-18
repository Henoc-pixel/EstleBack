from asgiref.sync import sync_to_async
from django.contrib.auth import get_user_model
from ninja import Router
from ninja.errors import HttpError
from .auth_helpers import AsyncAuthBearer, create_token
from .schemas import (
    LoginSchema,
    RegisterSchema,
    TokenResponseSchema,
    UpdateProfileSchema,
    UserOutSchema,
)

User = get_user_model()
router = Router(tags=["Authentification ESTLE"])


@router.post("/register", response={201: TokenResponseSchema})
async def register(request, data: RegisterSchema):
    exists = await User.objects.filter(email=data.email.lower()).aexists()
    if exists:
        raise HttpError(400, "Un compte avec cette adresse e-mail existe déjà.")

    user = await sync_to_async(User.objects.create_user)(
        email=data.email.lower(),
        password=data.password,
        first_name=data.first_name,
        last_name=data.last_name,
        phone_number=data.phone_number,
        default_city=data.default_city,
        default_commune=data.default_commune,
        default_address=data.default_address,
    )

    access_token = create_token(user.id, token_type="access")
    refresh_token = create_token(user.id, token_type="refresh")

    return 201, {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "Bearer",
        "user": user,
    }


@router.post("/login", response=TokenResponseSchema)
async def login(request, data: LoginSchema):
    try:
        user = await User.objects.aget(email=data.email.lower())
    except User.DoesNotExist:
        raise HttpError(401, "Identifiants invalides.")

    valid = await sync_to_async(user.check_password)(data.password)
    if not valid:
        raise HttpError(401, "Identifiants invalides.")

    if not user.is_active:
        raise HttpError(403, "Ce compte a été désactivé.")

    access_token = create_token(user.id, token_type="access")
    refresh_token = create_token(user.id, token_type="refresh")

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "Bearer",
        "user": user,
    }


@router.get("/me", response=UserOutSchema, auth=AsyncAuthBearer())
async def get_me(request):
    return request.auth


@router.put("/me", response=UserOutSchema, auth=AsyncAuthBearer())
async def update_me(request, data: UpdateProfileSchema):
    user = request.auth
    user.first_name = data.first_name
    user.last_name = data.last_name
    user.phone_number = data.phone_number
    user.default_city = data.default_city
    user.default_commune = data.default_commune
    user.default_address = data.default_address
    await user.asave()
    return user
