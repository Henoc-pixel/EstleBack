from django.contrib import admin
from .models import (
    Collection,
    Order,
    OrderItem,
    PaymentMethodConfig,
    Product,
    ProductImage,
    ProductVariant,
    SiteContent,
)


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1


@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "slug", "showcase_index", "is_featured")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "sku",
        "category",
        "collection",
        "price_fcfa",
        "is_new_arrival",
        "is_out_of_stock_override",
        "is_active",
    )
    list_filter = ("category", "collection", "is_new_arrival", "is_out_of_stock_override", "is_active")
    search_fields = ("name", "sku", "description")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [ProductImageInline, ProductVariantInline]


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("order_number", "full_name", "phone", "city", "commune", "payment_method", "status", "total_fcfa", "created_at")
    list_filter = ("status", "payment_method", "delivery_zone_type", "city")
    search_fields = ("order_number", "full_name", "email", "phone")
    inlines = [OrderItemInline]


@admin.register(PaymentMethodConfig)
class PaymentMethodConfigAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "is_active", "badge_label", "display_order")
    list_editable = ("is_active", "badge_label", "display_order")


@admin.register(SiteContent)
class SiteContentAdmin(admin.ModelAdmin):
    list_display = ("key", "title", "subtitle", "updated_at")
