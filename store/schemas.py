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
    payment_method: str
    payment_reference: str
    payment_status: str
    status: str
    subtotal_fcfa: int
    shipping_fee_fcfa: int
    total_fcfa: int
    notes: str
    created_at: datetime
    items: List[OrderItemOutSchema]


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
