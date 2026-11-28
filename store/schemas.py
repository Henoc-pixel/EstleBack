from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class ProductImageSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    image_url: str
    view_type: str
    caption: str
    display_order: int


class ProductVariantSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    size: str
    color_name: str
    color_hex: str
    stock: int
    sku_variant: str


class CollectionSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    name: str
    slug: str
    subtitle: str
    description: str
    editorial_quote: str
    hero_image: str
    secondary_image: str
    accent_color: str
    showcase_index: int
    shader_type: str
    is_featured: bool
    product_count: int = 0


class ProductSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    collection_id: int
    collection_name: str
    collection_slug: str
    category: str
    name: str
    slug: str
    sku: str
    price_fcfa: int
    compare_at_price_fcfa: Optional[int] = None
    short_description: str
    description: str
    fabric_specs: str
    cut_specs: str
    care_instructions: str
    shader_preset: str
    is_new_arrival: bool
    is_featured: bool
    is_out_of_stock_override: bool
    is_active: bool
    in_stock: bool
    total_stock: int
    average_rating: float = 0.0
    review_count: int = 0
    primary_image: str
    secondary_image: str
    images: List[ProductImageSchema]
    variants: List[ProductVariantSchema]
    created_at: datetime


class CollectionDetailSchema(CollectionSchema):
    products: List[ProductSchema]


class PaymentMethodConfigSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    name: str
    description: str
    instructions: str
    badge_label: str
    is_active: bool
    display_order: int


class SiteContentSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    key: str
    title: str
    subtitle: str
    body: str
    cta_label: str
    updated_at: datetime


# --- COMMANDES CÔTE D'IVOIRE ---
class OrderItemCreateSchema(BaseModel):
    product_id: int
    variant_id: Optional[int] = None
    size: str = "L"
    color_name: str = "Obsidian Black"
    quantity: int = Field(..., ge=1)


class OrderCreateSchema(BaseModel):
    email: str = Field(..., pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    full_name: str = Field(..., min_length=2)
    phone: str = Field(..., min_length=8)
    delivery_zone_type: str = "ABIDJAN"  # ABIDJAN | INTERIEUR
    city: str = "Abidjan"
    commune: str = "Cocody"
    address_details: str = Field(..., min_length=3)
    landmark: str = ""
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    payment_method: str = "WAVE"
    payment_reference: str = ""
    notes: str = ""
    items: List[OrderItemCreateSchema]


class OrderItemOutSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    product_id: Optional[int] = None
    variant_id: Optional[int] = None
    product_name: str
    product_slug: str
    image_url: str
    size: str
    color_name: str
    unit_price_fcfa: int
    quantity: int
    subtotal_fcfa: int


class OrderOutSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    order_number: str
    email: str
    full_name: str
    phone: str
    delivery_zone_type: str
    city: str
    commune: str
    address_details: str
    landmark: str = ""
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    payment_method: str
    payment_reference: str
    payment_status: str
    status: str
    subtotal_fcfa: int
    shipping_fee_fcfa: int
    total_fcfa: int
    notes: str
    delivered_at: Optional[datetime] = None
    created_at: datetime
    items: List[OrderItemOutSchema]


# --- NOTES & AVIS CLIENTS (MODÉRATION ADMIN & DÉLAI 30 JOURS) ---
class ReviewCreateSchema(BaseModel):
    order_item_id: int
    rating: int = Field(..., ge=1, le=5)
    title: str = Field(default="", max_length=140)
    comment: str = Field(..., min_length=5, max_length=1500)


class ReviewOutSchema(BaseModel):
    id: int
    product_id: int
    product_name: str
    product_slug: str
    product_image: str
    order_number: str
    author_name: str
    author_email: str = ""
    rating: int
    title: str
    comment: str
    status: str
    moderation_note: str = ""
    moderated_by_email: str = ""
    moderated_at: Optional[datetime] = None
    created_at: datetime


class EligibleReviewItemSchema(BaseModel):
    order_item_id: int
    order_number: str
    size: str
    color_name: str
    delivered_at: datetime
    days_remaining: int


class ProductReviewsSummarySchema(BaseModel):
    average_rating: float
    review_count: int
    distribution: dict
    reviews: List[ReviewOutSchema]
    can_review: bool
    eligible_items: List[EligibleReviewItemSchema]
    my_reviews: List[ReviewOutSchema]


class AdminReviewModerateSchema(BaseModel):
    status: str = Field(..., pattern=r"^(APPROVED|REJECTED|PENDING)$")
    moderation_note: str = Field(default="", max_length=255)


# --- ADMIN CRUD SCHEMAS ---
class AdminImageInputSchema(BaseModel):
    image_url: str
    view_type: str = "FRONT"
    caption: str = ""
    display_order: int = 0


class AdminVariantInputSchema(BaseModel):
    id: Optional[int] = None
    size: str
    color_name: str = "Obsidian Black"
    color_hex: str = "#080808"
    stock: int = Field(default=10, ge=0)


class AdminProductWriteSchema(BaseModel):
    collection_id: int
    category: str = "STREETWEAR"
    name: str
    slug: Optional[str] = None
    sku: Optional[str] = None
    price_fcfa: int = Field(..., gt=0)
    compare_at_price_fcfa: Optional[int] = None
    short_description: str = ""
    description: str
    fabric_specs: str = "Coton lourd 520 GSM • Teinture obsidienne"
    cut_specs: str = "Coupe Architecturale Oversize"
    care_instructions: str = "Lavage à froid 30°C à l'envers"
    shader_preset: str = "cloth"
    is_new_arrival: bool = False
    is_featured: bool = True
    is_out_of_stock_override: bool = False
    is_active: bool = True
    images: List[AdminImageInputSchema] = []
    variants: List[AdminVariantInputSchema] = []


class AdminVariantStockPatchSchema(BaseModel):
    stock: int = Field(..., ge=0)


class AdminCollectionWriteSchema(BaseModel):
    code: str = "01 — STREETWEAR"
    name: str
    slug: Optional[str] = None
    subtitle: str = ""
    description: str
    editorial_quote: str = ""
    hero_image: str
    secondary_image: str = ""
    accent_color: str = "#0E2920"
    showcase_index: int = 1
    shader_type: str = "cloth"
    is_featured: bool = True


class AdminOrderStatusPatchSchema(BaseModel):
    status: str
    payment_status: Optional[str] = None


class AdminSiteContentPatchSchema(BaseModel):
    title: str
    subtitle: str = ""
    body: str
    cta_label: str = ""


class AdminPaymentToggleSchema(BaseModel):
    is_active: bool
    badge_label: Optional[str] = None
    instructions: Optional[str] = None


class LookPieceOutSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    role: str
    product_id: Optional[int] = None
    product_slug: Optional[str] = None
    name: str
    price_fcfa: int
    image: str
    product: Optional[ProductSchema] = None


class LookOutSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    index: int
    code: str
    title: str
    season: str
    silhouette_image: str
    styling_notes: str
    coordinates: str
    display_order: int
    is_active: bool
    pieces: List[LookPieceOutSchema] = []


class AdminLookPieceWriteSchema(BaseModel):
    id: Optional[int] = None
    role: str = "TOP"
    product_id: Optional[int] = None
    fallback_name: str = ""
    fallback_price_fcfa: int = 0
    fallback_image: str = ""
    order: int = 0


class AdminLookWriteSchema(BaseModel):
    code: str = "LOOK 01"
    title: str
    season: str = "AW26 • ABIDJAN STUDIO"
    silhouette_image: str
    styling_notes: str = ""
    coordinates: str = "5.3599° N • 4.0083° W"
    display_order: int = 0
    is_active: bool = True
    pieces: List[AdminLookPieceWriteSchema] = []

