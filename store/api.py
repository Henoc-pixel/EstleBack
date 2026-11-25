import uuid
from typing import List, Optional
from asgiref.sync import sync_to_async
from django.db import transaction
from django.db.models import Q
from django.utils.text import slugify
from ninja import Router
from ninja.errors import HttpError
from accounts.auth_helpers import AsyncAdminAuthBearer, AsyncAuthBearer, decode_token
from django.contrib.auth import get_user_model
from .models import (
    Collection,
    Order,
    OrderItem,
    PaymentMethodConfig,
    Product,
    ProductImage,
    ProductVariant,
    SiteContent,
    Look,
    LookPiece,
)
from .schemas import (
    AdminCollectionWriteSchema,
    AdminLookWriteSchema,
    AdminOrderStatusPatchSchema,
    AdminPaymentToggleSchema,
    AdminProductWriteSchema,
    AdminSiteContentPatchSchema,
    AdminVariantStockPatchSchema,
    CollectionDetailSchema,
    CollectionSchema,
    LookOutSchema,
    OrderCreateSchema,
    OrderOutSchema,
    PaymentMethodConfigSchema,
    ProductSchema,
    SiteContentSchema,
)

User = get_user_model()
router = Router(tags=["ESTLE Storefront & Admin API"])


async def _serialize_product(p: Product) -> dict:
    images = [img async for img in ProductImage.objects.filter(product_id=p.id).order_by("display_order", "id")]
    variants = [v async for v in ProductVariant.objects.filter(product_id=p.id).order_by("id")]

    total_stock = 0 if p.is_out_of_stock_override else sum(v.stock for v in variants)
    in_stock = (not p.is_out_of_stock_override) and (total_stock > 0)

    default_img = "https://images.unsplash.com/photo-1509631179647-0177331693ae?w=1200&auto=format&fit=crop&q=80"
    primary_image = images[0].image_url if len(images) > 0 else default_img
    secondary_image = images[1].image_url if len(images) > 1 else primary_image

    return {
        "id": p.id,
        "collection_id": p.collection_id,
        "collection_name": p.collection.name,
        "collection_slug": p.collection.slug,
        "category": p.category,
        "name": p.name,
        "slug": p.slug,
        "sku": p.sku,
        "price_fcfa": p.price_fcfa,
        "compare_at_price_fcfa": p.compare_at_price_fcfa,
        "short_description": p.short_description,
        "description": p.description,
        "fabric_specs": p.fabric_specs,
        "cut_specs": p.cut_specs,
        "care_instructions": p.care_instructions,
        "shader_preset": p.shader_preset,
        "is_new_arrival": p.is_new_arrival,
        "is_featured": p.is_featured,
        "is_out_of_stock_override": p.is_out_of_stock_override,
        "is_active": p.is_active,
        "in_stock": in_stock,
        "total_stock": total_stock,
        "primary_image": primary_image,
        "secondary_image": secondary_image,
        "images": images,
        "variants": [
            {
                "id": v.id,
                "size": v.size,
                "color_name": v.color_name,
                "color_hex": v.color_hex,
                "stock": 0 if p.is_out_of_stock_override else v.stock,
                "sku_variant": v.sku_variant,
            }
            for v in variants
        ],
        "created_at": p.created_at,
    }


async def _serialize_order(order: Order) -> dict:
    items = [it async for it in OrderItem.objects.filter(order_id=order.id).order_by("id")]
    return {
        "id": order.id,
        "order_number": order.order_number,
        "email": order.email,
        "full_name": order.full_name,
        "phone": order.phone,
        "delivery_zone_type": order.delivery_zone_type,
        "city": order.city,
        "commune": order.commune,
        "address_details": order.address_details,
        "payment_method": order.payment_method,
        "payment_reference": order.payment_reference,
        "payment_status": order.payment_status,
        "status": order.status,
        "subtotal_fcfa": order.subtotal_fcfa,
        "shipping_fee_fcfa": order.shipping_fee_fcfa,
        "total_fcfa": order.total_fcfa,
        "notes": order.notes,
        "created_at": order.created_at,
        "items": items,
    }


async def _serialize_look(look: Look, index: int) -> dict:
    pieces_qs = LookPiece.objects.filter(look_id=look.id).select_related("product", "product__collection").order_by("order", "id")
    pieces_data = []
    async for p in pieces_qs:
        prod = p.product
        prod_data = await _serialize_product(prod) if prod else None
        display_name = prod.name if prod else (p.fallback_name or "Pièce ESTLE")
        display_price = prod.price_fcfa if prod else p.fallback_price_fcfa
        display_img = prod_data["primary_image"] if prod_data else (p.fallback_image or "")

        pieces_data.append({
            "id": p.id,
            "role": p.role,
            "product_id": prod.id if prod else None,
            "product_slug": prod.slug if prod else None,
            "name": display_name,
            "price_fcfa": display_price,
            "image": display_img,
            "product": prod_data,
        })

    return {
        "id": look.id,
        "index": index,
        "code": look.code,
        "title": look.title,
        "season": look.season,
        "silhouette_image": look.silhouette_image,
        "styling_notes": look.styling_notes,
        "coordinates": look.coordinates,
        "display_order": look.display_order,
        "is_active": look.is_active,
        "pieces": pieces_data,
    }



def _calculate_shipping_fcfa(zone_type: str, city: str, commune: str, subtotal: int) -> int:
    if zone_type.upper() == "ABIDJAN" and subtotal >= 180000:
        return 0
    if zone_type.upper() == "INTERIEUR" or city.lower() != "abidjan":
        return 5000
    peripherie = {"yopougon", "abobo", "bingerville", "anyama", "grand-bassam", "songon"}
    if commune.strip().lower() in peripherie:
        return 3000
    return 2000


# ============================================================================
# 1. CATALOGUE PUBLIC (PRODUITS & COLLECTIONS) — 100% ASYNC
# ============================================================================

@router.get("/products", response=List[ProductSchema])
async def list_products(
    request,
    category: Optional[str] = None,
    collection_slug: Optional[str] = None,
    size: Optional[str] = None,
    color: Optional[str] = None,
    min_price: Optional[int] = None,
    max_price: Optional[int] = None,
    new_arrivals: Optional[bool] = None,
    search: Optional[str] = None,
):
    qs = Product.objects.filter(is_active=True).select_related("collection")

    if category and category.upper() != "ALL":
        qs = qs.filter(category=category.upper())
    if collection_slug and collection_slug.lower() != "all":
        qs = qs.filter(collection__slug=collection_slug)
    if min_price is not None:
        qs = qs.filter(price_fcfa__gte=min_price)
    if max_price is not None:
        qs = qs.filter(price_fcfa__lte=max_price)
    if new_arrivals is True:
        qs = qs.filter(is_new_arrival=True)
    if search:
        qs = qs.filter(
            Q(name__icontains=search)
            | Q(description__icontains=search)
            | Q(short_description__icontains=search)
            | Q(sku__icontains=search)
        )
    if size and size.upper() != "ALL":
        qs = qs.filter(variants__size__iexact=size, variants__stock__gt=0).distinct()
    if color and color.upper() != "ALL":
        qs = qs.filter(variants__color_name__icontains=color).distinct()

    results = []
    async for p in qs:
        results.append(await _serialize_product(p))
    return results


@router.get("/products/{slug}", response=ProductSchema)
async def get_product(request, slug: str):
    try:
        p = await Product.objects.select_related("collection").aget(slug=slug, is_active=True)
    except Product.DoesNotExist:
        raise HttpError(404, "Pièce ESTLE introuvable.")
    return await _serialize_product(p)


@router.get("/collections", response=List[CollectionSchema])
async def list_collections(request):
    out = []
    async for c in Collection.objects.all().order_by("showcase_index", "id"):
        count = await Product.objects.filter(collection_id=c.id, is_active=True).acount()
        out.append({
            "id": c.id,
            "code": c.code,
            "name": c.name,
            "slug": c.slug,
            "subtitle": c.subtitle,
            "description": c.description,
            "editorial_quote": c.editorial_quote,
            "hero_image": c.hero_image,
            "secondary_image": c.secondary_image,
            "accent_color": c.accent_color,
            "showcase_index": c.showcase_index,
            "shader_type": c.shader_type,
            "is_featured": c.is_featured,
            "product_count": count,
        })
    return out


@router.get("/collections/{slug}", response=CollectionDetailSchema)
async def get_collection_detail(request, slug: str):
    try:
        c = await Collection.objects.aget(slug=slug)
    except Collection.DoesNotExist:
        raise HttpError(404, "Collection introuvable.")

    products = []
    async for p in Product.objects.filter(collection_id=c.id, is_active=True).select_related("collection"):
        products.append(await _serialize_product(p))

    return {
        "id": c.id,
        "code": c.code,
        "name": c.name,
        "slug": c.slug,
        "subtitle": c.subtitle,
        "description": c.description,
        "editorial_quote": c.editorial_quote,
        "hero_image": c.hero_image,
        "secondary_image": c.secondary_image,
        "accent_color": c.accent_color,
        "showcase_index": c.showcase_index,
        "shader_type": c.shader_type,
        "is_featured": c.is_featured,
        "product_count": len(products),
        "products": products,
    }


@router.get("/site-content", response=List[SiteContentSchema])
async def list_site_content(request):
    return [item async for item in SiteContent.objects.all().order_by("key")]


@router.get("/payment-methods", response=List[PaymentMethodConfigSchema])
async def list_payment_methods(request):
    return [pm async for pm in PaymentMethodConfig.objects.all().order_by("display_order", "id")]


# ============================================================================
# 2. COMMANDES & CHECKOUT CÔTE D'IVOIRE (TRANSACTION ATOMIQUE)
# ============================================================================

def _execute_atomic_order(data: OrderCreateSchema, user_id: Optional[int]) -> Order:
    with transaction.atomic():
        pm = PaymentMethodConfig.objects.filter(code=data.payment_method.upper()).first()
        if not pm or not pm.is_active:
            raise HttpError(
                400,
                f"Le moyen de paiement '{data.payment_method}' n'est pas encore activé. Veuillez choisir un moyen opérationnel.",
            )

        subtotal_fcfa = 0
        prepared_items = []

        for req_item in data.items:
            product = (
                Product.objects.select_for_update()
                .filter(id=req_item.product_id, is_active=True)
                .first()
            )
            if not product:
                raise HttpError(400, f"Pièce #{req_item.product_id} introuvable ou indisponible.")
            if product.is_out_of_stock_override:
                raise HttpError(400, f"La pièce '{product.name}' est actuellement en rupture de stock.")

            variant = None
            if req_item.variant_id:
                variant = (
                    ProductVariant.objects.select_for_update()
                    .filter(id=req_item.variant_id, product_id=product.id)
                    .first()
                )
            if not variant:
                variant = (
                    ProductVariant.objects.select_for_update()
                    .filter(product_id=product.id, size__iexact=req_item.size)
                    .first()
                )
            if not variant:
                variant = ProductVariant.objects.select_for_update().filter(product_id=product.id).first()

            if not variant or variant.stock < req_item.quantity:
                avail = variant.stock if variant else 0
                raise HttpError(
                    400,
                    f"Stock insuffisant pour '{product.name}' (Taille {req_item.size}). Disponible : {avail}.",
                )

            variant.stock -= req_item.quantity
            variant.save(update_fields=["stock"])

            first_img = ProductImage.objects.filter(product_id=product.id).order_by("display_order").first()
            img_url = first_img.image_url if first_img else ""

            line_total = product.price_fcfa * req_item.quantity
            subtotal_fcfa += line_total

            prepared_items.append({
                "product": product,
                "variant": variant,
                "product_name": product.name,
                "product_slug": product.slug,
                "image_url": img_url,
                "size": variant.size,
                "color_name": variant.color_name,
                "unit_price_fcfa": product.price_fcfa,
                "quantity": req_item.quantity,
                "subtotal_fcfa": line_total,
            })

        shipping_fee = _calculate_shipping_fcfa(
            data.delivery_zone_type, data.city, data.commune, subtotal_fcfa
        )
        total_fcfa = subtotal_fcfa + shipping_fee

        order = Order.objects.create(
            user_id=user_id,
            email=data.email.lower(),
            full_name=data.full_name,
            phone=data.phone,
            delivery_zone_type=data.delivery_zone_type.upper(),
            city=data.city,
            commune=data.commune,
            address_details=data.address_details,
            payment_method=pm.code,
            payment_reference=data.payment_reference or f"{pm.code}-{uuid.uuid4().hex[:6].upper()}",
            payment_status=Order.PaymentStatusChoices.PAID,
            status=Order.StatusChoices.CONFIRMED,
            subtotal_fcfa=subtotal_fcfa,
            shipping_fee_fcfa=shipping_fee,
            total_fcfa=total_fcfa,
            notes=data.notes,
        )

        for item in prepared_items:
            OrderItem.objects.create(order=order, **item)

        return order


@router.post("/orders", response={201: OrderOutSchema})
async def create_order(request, data: OrderCreateSchema):
    if not data.items:
        raise HttpError(400, "Votre sélection est vide.")

    user_id = None
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        token = auth_header.split(" ", 1)[1].strip()
        payload = decode_token(token)
        if payload and payload.get("token_type") == "access":
            user_id = payload.get("user_id")

    order = await sync_to_async(_execute_atomic_order, thread_sensitive=True)(data, user_id)
    return 201, await _serialize_order(order)


@router.get("/orders/my", response=List[OrderOutSchema], auth=AsyncAuthBearer())
async def list_my_orders(request):
    user = request.auth
    orders = []
    async for o in Order.objects.filter(Q(user_id=user.id) | Q(email__iexact=user.email)).order_by("-created_at"):
        orders.append(await _serialize_order(o))
    return orders


@router.get("/orders/{order_number}", response=OrderOutSchema)
async def get_order_by_number(request, order_number: str):
    try:
        order = await Order.objects.aget(order_number=order_number)
    except Order.DoesNotExist:
        raise HttpError(404, "Commande introuvable.")
    return await _serialize_order(order)


# ============================================================================
# 3. ESPACE ADMINISTRATEUR SÉCURISÉ JWT (/api/v1/admin/...)
# ============================================================================

@router.get("/admin/products", response=List[ProductSchema], auth=AsyncAdminAuthBearer())
async def admin_list_products(request):
    out = []
    async for p in Product.objects.all().select_related("collection").order_by("-created_at"):
        out.append(await _serialize_product(p))
    return out


@router.post("/admin/products", response={201: ProductSchema}, auth=AsyncAdminAuthBearer())
async def admin_create_product(request, data: AdminProductWriteSchema):
    slug = data.slug or slugify(data.name)
    if await Product.objects.filter(slug=slug).aexists():
        slug = f"{slug}-{uuid.uuid4().hex[:4]}"

    sku = data.sku or f"ESTLE-{uuid.uuid4().hex[:6].upper()}"
    p = await Product.objects.acreate(
        collection_id=data.collection_id,
        category=data.category,
        name=data.name,
        slug=slug,
        sku=sku,
        price_fcfa=data.price_fcfa,
        compare_at_price_fcfa=data.compare_at_price_fcfa,
        short_description=data.short_description,
        description=data.description,
        fabric_specs=data.fabric_specs,
        cut_specs=data.cut_specs,
        care_instructions=data.care_instructions,
        shader_preset=data.shader_preset,
        is_new_arrival=data.is_new_arrival,
        is_featured=data.is_featured,
        is_out_of_stock_override=data.is_out_of_stock_override,
        is_active=data.is_active,
    )

    for idx, img in enumerate(data.images):
        await ProductImage.objects.acreate(
            product=p,
            image_url=img.image_url,
            view_type=img.view_type,
            caption=img.caption,
            display_order=img.display_order or idx,
        )

    variants_input = data.variants or [
        AdminVariantStockPatchSchema(stock=10)  # fallback if empty
    ]
    if data.variants:
        for v in data.variants:
            await ProductVariant.objects.acreate(
                product=p,
                size=v.size,
                color_name=v.color_name,
                color_hex=v.color_hex,
                stock=v.stock,
                sku_variant=f"{sku}-{v.size}-{uuid.uuid4().hex[:3].upper()}",
            )
    else:
        for sz in ["S", "M", "L", "XL"]:
            await ProductVariant.objects.acreate(
                product=p,
                size=sz,
                color_name="Obsidian Black",
                color_hex="#080808",
                stock=8,
                sku_variant=f"{sku}-{sz}",
            )

    p_full = await Product.objects.select_related("collection").aget(id=p.id)
    return 201, await _serialize_product(p_full)


@router.put("/admin/products/{product_id}", response=ProductSchema, auth=AsyncAdminAuthBearer())
async def admin_update_product(request, product_id: int, data: AdminProductWriteSchema):
    try:
        p = await Product.objects.aget(id=product_id)
    except Product.DoesNotExist:
        raise HttpError(404, "Produit introuvable.")

    p.collection_id = data.collection_id
    p.category = data.category
    p.name = data.name
    p.price_fcfa = data.price_fcfa
    p.compare_at_price_fcfa = data.compare_at_price_fcfa
    p.short_description = data.short_description
    p.description = data.description
    p.fabric_specs = data.fabric_specs
    p.cut_specs = data.cut_specs
    p.care_instructions = data.care_instructions
    p.shader_preset = data.shader_preset
    p.is_new_arrival = data.is_new_arrival
    p.is_featured = data.is_featured
    p.is_out_of_stock_override = data.is_out_of_stock_override
    p.is_active = data.is_active
    await p.asave()

    if data.images:
        await ProductImage.objects.filter(product_id=p.id).adelete()
        for idx, img in enumerate(data.images):
            await ProductImage.objects.acreate(
                product=p,
                image_url=img.image_url,
                view_type=img.view_type,
                caption=img.caption,
                display_order=img.display_order or idx,
            )

    if data.variants:
        await ProductVariant.objects.filter(product_id=p.id).adelete()
        for v in data.variants:
            await ProductVariant.objects.acreate(
                product=p,
                size=v.size,
                color_name=v.color_name,
                color_hex=v.color_hex,
                stock=v.stock,
                sku_variant=f"{p.sku}-{v.size}-{uuid.uuid4().hex[:3].upper()}",
            )

    p_full = await Product.objects.select_related("collection").aget(id=p.id)
    return await _serialize_product(p_full)


@router.post("/admin/products/{product_id}/toggle-stock", response=ProductSchema, auth=AsyncAdminAuthBearer())
async def admin_toggle_product_out_of_stock(request, product_id: int):
    try:
        p = await Product.objects.select_related("collection").aget(id=product_id)
    except Product.DoesNotExist:
        raise HttpError(404, "Produit introuvable.")

    p.is_out_of_stock_override = not p.is_out_of_stock_override
    await p.asave(update_fields=["is_out_of_stock_override"])
    return await _serialize_product(p)


@router.patch("/admin/variants/{variant_id}/stock", response=dict, auth=AsyncAdminAuthBearer())
async def admin_update_variant_stock(request, variant_id: int, data: AdminVariantStockPatchSchema):
    try:
        v = await ProductVariant.objects.aget(id=variant_id)
    except ProductVariant.DoesNotExist:
        raise HttpError(404, "Variante introuvable.")
    v.stock = data.stock
    await v.asave(update_fields=["stock"])
    return {"id": v.id, "stock": v.stock, "size": v.size, "color_name": v.color_name}


@router.delete("/admin/products/{product_id}", response=dict, auth=AsyncAdminAuthBearer())
async def admin_delete_product(request, product_id: int):
    await Product.objects.filter(id=product_id).adelete()
    return {"deleted": True, "id": product_id}


@router.post("/admin/collections", response={201: CollectionSchema}, auth=AsyncAdminAuthBearer())
async def admin_create_collection(request, data: AdminCollectionWriteSchema):
    slug = data.slug or slugify(data.name)
    if await Collection.objects.filter(slug=slug).aexists():
        slug = f"{slug}-{uuid.uuid4().hex[:4]}"

    c = await Collection.objects.acreate(
        code=data.code,
        name=data.name,
        slug=slug,
        subtitle=data.subtitle,
        description=data.description,
        editorial_quote=data.editorial_quote,
        hero_image=data.hero_image,
        secondary_image=data.secondary_image,
        accent_color=data.accent_color,
        showcase_index=data.showcase_index,
        shader_type=data.shader_type,
        is_featured=data.is_featured,
    )
    return 201, {
        "id": c.id,
        "code": c.code,
        "name": c.name,
        "slug": c.slug,
        "subtitle": c.subtitle,
        "description": c.description,
        "editorial_quote": c.editorial_quote,
        "hero_image": c.hero_image,
        "secondary_image": c.secondary_image,
        "accent_color": c.accent_color,
        "showcase_index": c.showcase_index,
        "shader_type": c.shader_type,
        "is_featured": c.is_featured,
        "product_count": 0,
    }


@router.put("/admin/collections/{collection_id}", response=CollectionSchema, auth=AsyncAdminAuthBearer())
async def admin_update_collection(request, collection_id: int, data: AdminCollectionWriteSchema):
    try:
        c = await Collection.objects.aget(id=collection_id)
    except Collection.DoesNotExist:
        raise HttpError(404, "Collection introuvable.")

    c.code = data.code
    c.name = data.name
    c.subtitle = data.subtitle
    c.description = data.description
    c.editorial_quote = data.editorial_quote
    c.hero_image = data.hero_image
    c.secondary_image = data.secondary_image
    c.accent_color = data.accent_color
    c.showcase_index = data.showcase_index
    c.shader_type = data.shader_type
    c.is_featured = data.is_featured
    await c.asave()

    count = await Product.objects.filter(collection_id=c.id, is_active=True).acount()
    return {
        "id": c.id,
        "code": c.code,
        "name": c.name,
        "slug": c.slug,
        "subtitle": c.subtitle,
        "description": c.description,
        "editorial_quote": c.editorial_quote,
        "hero_image": c.hero_image,
        "secondary_image": c.secondary_image,
        "accent_color": c.accent_color,
        "showcase_index": c.showcase_index,
        "shader_type": c.shader_type,
        "is_featured": c.is_featured,
        "product_count": count,
    }


@router.get("/admin/orders", response=List[OrderOutSchema], auth=AsyncAdminAuthBearer())
async def admin_list_orders(request):
    out = []
    async for o in Order.objects.all().order_by("-created_at"):
        out.append(await _serialize_order(o))
    return out


@router.patch("/admin/orders/{order_id}/status", response=OrderOutSchema, auth=AsyncAdminAuthBearer())
async def admin_update_order_status(request, order_id: int, data: AdminOrderStatusPatchSchema):
    try:
        o = await Order.objects.aget(id=order_id)
    except Order.DoesNotExist:
        raise HttpError(404, "Commande introuvable.")

    o.status = data.status
    if data.payment_status:
        o.payment_status = data.payment_status
    await o.asave()
    return await _serialize_order(o)


@router.put("/admin/site-content/{key}", response=SiteContentSchema, auth=AsyncAdminAuthBearer())
async def admin_update_site_content(request, key: str, data: AdminSiteContentPatchSchema):
    item, created = await SiteContent.objects.aget_or_create(
        key=key,
        defaults={
            "title": data.title,
            "subtitle": data.subtitle,
            "body": data.body,
            "cta_label": data.cta_label,
        },
    )
    if not created:
        item.title = data.title
        item.subtitle = data.subtitle
        item.body = data.body
        item.cta_label = data.cta_label
        await item.asave()
    return item


@router.patch("/admin/payment-methods/{code}", response=PaymentMethodConfigSchema, auth=AsyncAdminAuthBearer())
async def admin_toggle_payment_method(request, code: str, data: AdminPaymentToggleSchema):
    try:
        pm = await PaymentMethodConfig.objects.aget(code=code.upper())
    except PaymentMethodConfig.DoesNotExist:
        raise HttpError(404, "Passerelle de paiement introuvable.")

    pm.is_active = data.is_active
    if data.badge_label is not None:
        pm.badge_label = data.badge_label
    if data.instructions is not None:
        pm.instructions = data.instructions
    await pm.asave()
    return pm


# ============================================================================
# 5. LOOKS ÉDITORIAUX & SILHOUETTES "TRY THE LOOK" (PUBLIC & ADMIN)
# ============================================================================

@router.get("/looks", response=List[LookOutSchema])
async def list_looks(request):
    looks = [l async for l in Look.objects.filter(is_active=True).order_by("display_order", "id")]
    result = []
    for idx, look in enumerate(looks):
        result.append(await _serialize_look(look, idx))
    return result


@router.get("/admin/looks", response=List[LookOutSchema], auth=AsyncAdminAuthBearer())
async def list_admin_looks(request):
    looks = [l async for l in Look.objects.all().order_by("display_order", "id")]
    result = []
    for idx, look in enumerate(looks):
        result.append(await _serialize_look(look, idx))
    return result


@router.post("/admin/looks", response={201: LookOutSchema}, auth=AsyncAdminAuthBearer())
async def create_look(request, payload: AdminLookWriteSchema):
    @sync_to_async
    def _create():
        with transaction.atomic():
            look = Look.objects.create(
                code=payload.code,
                title=payload.title,
                season=payload.season,
                silhouette_image=payload.silhouette_image,
                styling_notes=payload.styling_notes,
                coordinates=payload.coordinates,
                display_order=payload.display_order,
                is_active=payload.is_active,
            )
            for idx, piece_data in enumerate(payload.pieces):
                LookPiece.objects.create(
                    look=look,
                    role=piece_data.role,
                    product_id=piece_data.product_id,
                    fallback_name=piece_data.fallback_name,
                    fallback_price_fcfa=piece_data.fallback_price_fcfa,
                    fallback_image=piece_data.fallback_image,
                    order=piece_data.order or idx,
                )
            return look

    look = await _create()
    count = await Look.objects.filter(id__lt=look.id, is_active=True).acount()
    data = await _serialize_look(look, count)
    return 201, data


@router.put("/admin/looks/{look_id}", response=LookOutSchema, auth=AsyncAdminAuthBearer())
async def update_look(request, look_id: int, payload: AdminLookWriteSchema):
    @sync_to_async
    def _update():
        with transaction.atomic():
            try:
                look = Look.objects.get(id=look_id)
            except Look.DoesNotExist:
                raise HttpError(404, "Look introuvable")
            look.code = payload.code
            look.title = payload.title
            look.season = payload.season
            look.silhouette_image = payload.silhouette_image
            look.styling_notes = payload.styling_notes
            look.coordinates = payload.coordinates
            look.display_order = payload.display_order
            look.is_active = payload.is_active
            look.save()

            if payload.pieces is not None:
                look.pieces.all().delete()
                for idx, piece_data in enumerate(payload.pieces):
                    LookPiece.objects.create(
                        look=look,
                        role=piece_data.role,
                        product_id=piece_data.product_id,
                        fallback_name=piece_data.fallback_name,
                        fallback_price_fcfa=piece_data.fallback_price_fcfa,
                        fallback_image=piece_data.fallback_image,
                        order=piece_data.order or idx,
                    )
            return look

    look = await _update()
    count = await Look.objects.filter(id__lt=look.id, is_active=True).acount()
    return await _serialize_look(look, count)


@router.delete("/admin/looks/{look_id}", response=dict, auth=AsyncAdminAuthBearer())
async def delete_look(request, look_id: int):
    @sync_to_async
    def _delete():
        deleted, _ = Look.objects.filter(id=look_id).delete()
        if not deleted:
            raise HttpError(404, "Look introuvable")
        return {"success": True, "message": "Look supprimé avec succès"}

    return await _delete()

