import uuid
from datetime import timedelta
from typing import Dict, List, Optional, Tuple
from asgiref.sync import sync_to_async
from django.db import transaction
from django.db.models import Avg, Count, Q
from django.utils import timezone
from django.utils.text import slugify
from ninja import Router
from ninja.errors import HttpError
from accounts.auth_helpers import (
    AsyncAdminAuthBearer,
    AsyncAuthBearer,
    create_notification,
    decode_token,
    record_audit,
    require_permission,
)
from django.contrib.auth import get_user_model
from .models import (
    Collection,
    Order,
    OrderItem,
    PaymentMethodConfig,
    Product,
    ProductImage,
    ProductReview,
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
    AdminReviewModerateSchema,
    AdminSiteContentPatchSchema,
    AdminVariantStockPatchSchema,
    CollectionDetailSchema,
    CollectionSchema,
    LookOutSchema,
    OrderCreateSchema,
    OrderOutSchema,
    PaymentMethodConfigSchema,
    ProductReviewsSummarySchema,
    ProductSchema,
    ReviewCreateSchema,
    ReviewOutSchema,
    SiteContentSchema,
)

User = get_user_model()
router = Router(tags=["ESTLE Storefront & Admin API"])


async def _get_rating_stats_map(product_ids: List[int]) -> Dict[int, Tuple[float, int]]:
    if not product_ids:
        return {}

    def _query():
        rows = (
            ProductReview.objects.filter(
                product_id__in=product_ids,
                status=ProductReview.StatusChoices.APPROVED,
            )
            .values("product_id")
            .annotate(avg=Avg("rating"), cnt=Count("id"))
        )
        return {
            r["product_id"]: (round(float(r["avg"] or 0.0), 1), int(r["cnt"] or 0))
            for r in rows
        }

    return await sync_to_async(_query)()


async def _serialize_product(
    p: Product,
    rating_map: Optional[Dict[int, Tuple[float, int]]] = None,
) -> dict:
    prefetched = getattr(p, "_prefetched_objects_cache", {})
    if "images" in prefetched:
        images = sorted(list(prefetched["images"]), key=lambda img: (img.display_order, img.id))
    else:
        images = [img async for img in ProductImage.objects.filter(product_id=p.id).order_by("display_order", "id")]

    if "variants" in prefetched:
        variants = sorted(list(prefetched["variants"]), key=lambda v: v.id)
    else:
        variants = [v async for v in ProductVariant.objects.filter(product_id=p.id).order_by("id")]

    total_stock = 0 if p.is_out_of_stock_override else sum(v.stock for v in variants)
    in_stock = (not p.is_out_of_stock_override) and (total_stock > 0)

    if rating_map is not None:
        avg_rating, rev_count = rating_map.get(p.id, (0.0, 0))
    else:
        single_map = await _get_rating_stats_map([p.id])
        avg_rating, rev_count = single_map.get(p.id, (0.0, 0))

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
        "average_rating": avg_rating,
        "review_count": rev_count,
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
        "landmark": order.landmark,
        "latitude": order.latitude,
        "longitude": order.longitude,
        "payment_method": order.payment_method,
        "payment_reference": order.payment_reference,
        "payment_status": order.payment_status,
        "status": order.status,
        "subtotal_fcfa": order.subtotal_fcfa,
        "shipping_fee_fcfa": order.shipping_fee_fcfa,
        "total_fcfa": order.total_fcfa,
        "notes": order.notes,
        "delivered_at": order.delivered_at,
        "created_at": order.created_at,
        "items": items,
    }


async def _serialize_look(look: Look, index: int) -> dict:
    pieces_qs = (
        LookPiece.objects.filter(look_id=look.id)
        .select_related("product", "product__collection")
        .prefetch_related("product__images", "product__variants")
        .order_by("order", "id")
    )
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
    qs = Product.objects.filter(is_active=True).select_related("collection").prefetch_related("images", "variants")

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

    products = [p async for p in qs]
    rating_map = await _get_rating_stats_map([p.id for p in products])
    results = []
    for p in products:
        results.append(await _serialize_product(p, rating_map=rating_map))
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
    async for p in Product.objects.filter(collection_id=c.id, is_active=True).select_related("collection").prefetch_related("images", "variants"):
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
            landmark=data.landmark,
            latitude=data.latitude,
            longitude=data.longitude,
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

    await create_notification(
        audience="ADMIN",
        required_permission="orders.view",
        category="ORDER",
        title=f"Nouvelle commande #{order.order_number}",
        message=f"{order.full_name} — {order.total_fcfa:,} FCFA ({order.commune}, {order.city}).".replace(",", " "),
        link="/admin/orders",
    )
    if user_id:
        await create_notification(
            audience="CLIENT",
            recipient_id=user_id,
            category="ORDER",
            title=f"Commande #{order.order_number} confirmée",
            message=f"Votre commande de {order.total_fcfa:,} FCFA est confirmée et en préparation à Abidjan.".replace(",", " "),
            link="/account?section=orders",
        )
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
    require_permission(request.auth, "orders.manage")
    try:
        o = await Order.objects.aget(id=order_id)
    except Order.DoesNotExist:
        raise HttpError(404, "Commande introuvable.")

    prev_status = o.status
    o.status = data.status
    if data.payment_status:
        o.payment_status = data.payment_status
    if data.status == Order.StatusChoices.DELIVERED and not o.delivered_at:
        o.delivered_at = timezone.now()
    await o.asave()

    if o.user_id and prev_status != data.status:
        status_messages = {
            "CONFIRMED": ("Commande confirmée", f"Votre commande #{o.order_number} est confirmée par l'atelier ESTLE."),
            "SHIPPING": ("Commande en cours de livraison", f"Votre coursier ESTLE est en route pour la commande #{o.order_number}."),
            "DELIVERED": (
                "Commande livrée — Donnez votre avis",
                f"Votre commande #{o.order_number} a été livrée ! Vous disposez de 30 jours pour noter chaque article individuellement.",
            ),
            "CANCELLED": ("Commande annulée", f"Votre commande #{o.order_number} a été annulée."),
        }
        title, msg = status_messages.get(
            data.status,
            (f"Statut commande #{o.order_number}", f"Nouveau statut : {data.status}"),
        )
        await create_notification(
            audience="CLIENT",
            recipient_id=o.user_id,
            category="ORDER",
            title=title,
            message=msg,
            link="/account?section=orders",
        )

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


# ============================================================================
# 6. NOTES & AVIS CLIENTS (DÉLAI 30 JOURS POST-LIVRAISON + MODÉRATION ADMIN)
# ============================================================================

def _serialize_review(r: ProductReview, include_email: bool = False) -> dict:
    author_name = f"{r.user.first_name} {r.user.last_name}".strip() or r.user.email.split("@")[0]
    first_img = ""
    prefetched = getattr(r.product, "_prefetched_objects_cache", {})
    if "images" in prefetched and prefetched["images"]:
        first_img = prefetched["images"][0].image_url
    else:
        img_obj = r.product.images.first()
        first_img = img_obj.image_url if img_obj else ""

    return {
        "id": r.id,
        "product_id": r.product_id,
        "product_name": r.product.name,
        "product_slug": r.product.slug,
        "product_image": first_img,
        "order_number": r.order.order_number,
        "author_name": author_name,
        "author_email": r.user.email if include_email else "",
        "rating": r.rating,
        "title": r.title,
        "comment": r.comment,
        "status": r.status,
        "moderation_note": r.moderation_note,
        "moderated_by_email": r.moderated_by.email if r.moderated_by else "",
        "moderated_at": r.moderated_at,
        "created_at": r.created_at,
    }


@router.get("/products/{slug}/reviews", response=ProductReviewsSummarySchema)
async def get_product_reviews(request, slug: str):
    try:
        product = await Product.objects.aget(slug=slug, is_active=True)
    except Product.DoesNotExist:
        raise HttpError(404, "Article introuvable.")

    user_id = None
    user_email = ""
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        token = auth_header.split(" ", 1)[1].strip()
        payload = decode_token(token)
        if payload and payload.get("token_type") == "access":
            user_id = payload.get("user_id")
            try:
                u = await User.objects.aget(id=user_id, is_active=True)
                user_email = u.email
            except User.DoesNotExist:
                user_id = None

    def _fetch():
        approved_qs = (
            ProductReview.objects.filter(
                product_id=product.id,
                status=ProductReview.StatusChoices.APPROVED,
            )
            .select_related("user", "order", "product", "moderated_by")
            .prefetch_related("product__images")
            .order_by("-created_at")
        )
        approved_list = list(approved_qs)
        review_count = len(approved_list)
        avg_rating = (
            round(sum(r.rating for r in approved_list) / review_count, 1)
            if review_count > 0
            else 0.0
        )
        dist = {"5": 0, "4": 0, "3": 0, "2": 0, "1": 0}
        for r in approved_list:
            k = str(r.rating)
            if k in dist:
                dist[k] += 1

        eligible_items = []
        my_reviews = []
        if user_id:
            my_rev_qs = (
                ProductReview.objects.filter(product_id=product.id, user_id=user_id)
                .select_related("user", "order", "product", "moderated_by")
                .prefetch_related("product__images")
                .order_by("-created_at")
            )
            my_reviews = [_serialize_review(r, include_email=False) for r in my_rev_qs]

            now = timezone.now()
            order_items = (
                OrderItem.objects.filter(
                    product_id=product.id,
                    order__status=Order.StatusChoices.DELIVERED,
                )
                .filter(Q(order__user_id=user_id) | Q(order__email__iexact=user_email))
                .select_related("order")
                .order_by("-order__delivered_at", "-order__updated_at")
            )
            reviewed_item_ids = set(
                ProductReview.objects.filter(
                    product_id=product.id, user_id=user_id
                ).values_list("order_item_id", flat=True)
            )
            for oi in order_items:
                if oi.id in reviewed_item_ids:
                    continue
                delivered_ts = oi.order.delivered_at or oi.order.updated_at or oi.order.created_at
                deadline = delivered_ts + timedelta(days=30)
                if now <= deadline:
                    days_left = max(1, (deadline - now).days + 1)
                    eligible_items.append(
                        {
                            "order_item_id": oi.id,
                            "order_number": oi.order.order_number,
                            "size": oi.size,
                            "color_name": oi.color_name,
                            "delivered_at": delivered_ts,
                            "days_remaining": min(30, days_left),
                        }
                    )

        return {
            "average_rating": avg_rating,
            "review_count": review_count,
            "distribution": dist,
            "reviews": [_serialize_review(r, include_email=False) for r in approved_list],
            "can_review": len(eligible_items) > 0,
            "eligible_items": eligible_items,
            "my_reviews": my_reviews,
        }

    return await sync_to_async(_fetch)()


@router.post("/products/{slug}/reviews", response={201: ReviewOutSchema}, auth=AsyncAuthBearer())
async def create_product_review(request, slug: str, data: ReviewCreateSchema):
    user = request.auth
    try:
        product = await Product.objects.aget(slug=slug, is_active=True)
    except Product.DoesNotExist:
        raise HttpError(404, "Article introuvable.")

    def _create():
        try:
            oi = (
                OrderItem.objects.select_related("order")
                .filter(Q(order__user_id=user.id) | Q(order__email__iexact=user.email))
                .get(id=data.order_item_id, product_id=product.id)
            )
        except OrderItem.DoesNotExist:
            raise HttpError(
                403,
                "Vous ne pouvez noter cet article que si vous l'avez commandé et reçu.",
            )

        if oi.order.status != Order.StatusChoices.DELIVERED:
            raise HttpError(
                400,
                "Vous pourrez noter cet article dès que votre commande aura été livrée.",
            )

        delivered_ts = oi.order.delivered_at or oi.order.updated_at or oi.order.created_at
        if timezone.now() > delivered_ts + timedelta(days=30):
            raise HttpError(
                400,
                "Le délai de 30 jours après livraison pour noter cet article est expiré.",
            )

        if ProductReview.objects.filter(order_item_id=oi.id).exists():
            raise HttpError(400, "Vous avez déjà soumis une note pour cet article.")

        rev = ProductReview.objects.create(
            product=product,
            user=user,
            order=oi.order,
            order_item=oi,
            rating=data.rating,
            title=data.title.strip(),
            comment=data.comment.strip(),
            status=ProductReview.StatusChoices.PENDING,
        )
        rev = (
            ProductReview.objects.select_related("user", "order", "product", "moderated_by")
            .prefetch_related("product__images")
            .get(id=rev.id)
        )
        return _serialize_review(rev, include_email=False)

    created_data = await sync_to_async(_create)()

    await create_notification(
        audience="ADMIN",
        required_permission="reviews.manage",
        category="REVIEW",
        title=f"Nouvel avis à valider ({data.rating}★) — {product.name}",
        message=f"{created_data['author_name']} a laissé un avis sur {product.name} (Commande #{created_data['order_number']}).",
        link="/admin/reviews",
    )

    return 201, created_data


@router.get("/admin/reviews", response=List[ReviewOutSchema], auth=AsyncAdminAuthBearer())
async def admin_list_reviews(request, status: Optional[str] = None):
    require_permission(request.auth, "reviews.manage")

    def _fetch():
        qs = (
            ProductReview.objects.select_related("user", "order", "product", "moderated_by")
            .prefetch_related("product__images")
            .order_by("-created_at")
        )
        if status and status.upper() in ("PENDING", "APPROVED", "REJECTED"):
            qs = qs.filter(status=status.upper())
        return [_serialize_review(r, include_email=True) for r in qs]

    return await sync_to_async(_fetch)()


@router.patch("/admin/reviews/{review_id}", response=ReviewOutSchema, auth=AsyncAdminAuthBearer())
async def admin_moderate_review(request, review_id: int, data: AdminReviewModerateSchema):
    require_permission(request.auth, "reviews.manage")

    def _moderate():
        try:
            rev = (
                ProductReview.objects.select_related("user", "order", "product", "moderated_by")
                .prefetch_related("product__images")
                .get(id=review_id)
            )
        except ProductReview.DoesNotExist:
            raise HttpError(404, "Avis introuvable.")

        rev.status = data.status
        rev.moderation_note = data.moderation_note.strip()
        rev.moderated_by = request.auth
        rev.moderated_at = timezone.now()
        rev.save()
        return rev, _serialize_review(rev, include_email=True)

    rev, serialized = await sync_to_async(_moderate)()

    await record_audit(
        request.auth,
        "REVIEW_MODERATED",
        f"Avis #{rev.id} ({rev.rating}★ sur {rev.product.name}) → {rev.status}",
        "ProductReview",
        str(rev.id),
    )

    if rev.status == ProductReview.StatusChoices.APPROVED:
        await create_notification(
            audience="CLIENT",
            recipient_id=rev.user_id,
            category="REVIEW",
            title=f"Votre avis sur {rev.product.name} est publié !",
            message=f"Merci pour votre note de {rev.rating}★. Votre avis a été validé par notre équipe et est désormais visible.",
            link=f"/product/{rev.product.slug}#reviews",
        )
    elif rev.status == ProductReview.StatusChoices.REJECTED:
        note_suffix = f" Motif : {rev.moderation_note}" if rev.moderation_note else ""
        await create_notification(
            audience="CLIENT",
            recipient_id=rev.user_id,
            category="REVIEW",
            title=f"Votre avis sur {rev.product.name} n'a pas été retenu",
            message=f"Votre avis soumis pour {rev.product.name} n'a pas pu être publié.{note_suffix}",
            link=f"/product/{rev.product.slug}#reviews",
        )

    return serialized


@router.delete("/admin/reviews/{review_id}", auth=AsyncAdminAuthBearer())
async def admin_delete_review(request, review_id: int):
    require_permission(request.auth, "reviews.manage")
    deleted, _ = await ProductReview.objects.filter(id=review_id).adelete()
    if not deleted:
        raise HttpError(404, "Avis introuvable.")
    await record_audit(
        request.auth,
        "REVIEW_DELETED",
        f"Avis #{review_id} supprimé",
        "ProductReview",
        str(review_id),
    )
    return {"ok": True}


