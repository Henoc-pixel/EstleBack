import uuid
from django.conf import settings
from django.db import models


class Collection(models.Model):
    code = models.CharField(max_length=50, default="01 — STREETWEAR")
    name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=180, unique=True, db_index=True)
    subtitle = models.CharField(max_length=255, blank=True)
    description = models.TextField()
    editorial_quote = models.CharField(max_length=255, blank=True)
    hero_image = models.URLField(max_length=500)
    secondary_image = models.URLField(max_length=500, blank=True)
    accent_color = models.CharField(max_length=20, default="#0E2920")
    showcase_index = models.PositiveSmallIntegerField(default=1, db_index=True)
    shader_type = models.CharField(max_length=40, default="cloth")
    is_featured = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Collection"
        verbose_name_plural = "Collections"
        ordering = ["showcase_index", "name"]

    def __str__(self):
        return f"{self.code} : {self.name}"


class Product(models.Model):
    class CategoryChoices(models.TextChoices):
        STREETWEAR = "STREETWEAR", "01 — STREETWEAR"
        MEN = "MEN", "02 — MEN"
        COLLECTIONS = "COLLECTIONS", "03 — COLLECTIONS"
        NEW_ARRIVALS = "NEW_ARRIVALS", "04 — NEW ARRIVALS"

    collection = models.ForeignKey(
        Collection,
        related_name="products",
        on_delete=models.CASCADE,
        db_index=True,
    )
    category = models.CharField(
        max_length=30,
        choices=CategoryChoices.choices,
        default=CategoryChoices.STREETWEAR,
        db_index=True,
    )
    name = models.CharField(max_length=200, db_index=True)
    slug = models.SlugField(max_length=220, unique=True, db_index=True)
    sku = models.CharField(max_length=64, unique=True, db_index=True)
    price_fcfa = models.PositiveIntegerField(db_index=True)
    compare_at_price_fcfa = models.PositiveIntegerField(null=True, blank=True)
    short_description = models.CharField(max_length=255, blank=True)
    description = models.TextField()
    fabric_specs = models.CharField(
        max_length=255,
        default="Coton lourd 520 GSM • Teinture obsidienne • Finition main Abidjan",
    )
    cut_specs = models.CharField(
        max_length=255,
        default="Coupe Architecturale Oversize • Épaules structurées",
    )
    care_instructions = models.CharField(
        max_length=255,
        default="Lavage à froid 30°C à l'envers • Séchage à plat à l'ombre",
    )
    shader_preset = models.CharField(max_length=30, default="cloth")
    is_new_arrival = models.BooleanField(default=False, db_index=True)
    is_featured = models.BooleanField(default=True, db_index=True)
    is_out_of_stock_override = models.BooleanField(default=False, db_index=True)
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Pièce ESTLE"
        verbose_name_plural = "Pièces ESTLE"
        ordering = ["-is_featured", "-created_at"]

    def __str__(self):
        return f"{self.name} ({self.price_fcfa} FCFA)"


class ProductImage(models.Model):
    class ViewTypeChoices(models.TextChoices):
        FRONT = "FRONT", "Vue de Face"
        BACK = "BACK", "Vue de Dos"
        DETAIL = "DETAIL", "Gros Plan Coutures & Matière"
        LOOKBOOK = "LOOKBOOK", "Silhouette Éditoriale"

    product = models.ForeignKey(Product, related_name="images", on_delete=models.CASCADE)
    image_url = models.URLField(max_length=500)
    view_type = models.CharField(
        max_length=20, choices=ViewTypeChoices.choices, default=ViewTypeChoices.FRONT
    )
    caption = models.CharField(max_length=200, blank=True)
    display_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["display_order", "id"]

    def __str__(self):
        return f"{self.product.name} [{self.view_type}]"


class ProductVariant(models.Model):
    product = models.ForeignKey(Product, related_name="variants", on_delete=models.CASCADE)
    size = models.CharField(max_length=15, db_index=True)  # S, M, L, XL, XXL, OS
    color_name = models.CharField(max_length=60, default="Obsidian Black", db_index=True)
    color_hex = models.CharField(max_length=15, default="#080808")
    stock = models.PositiveIntegerField(default=10)
    sku_variant = models.CharField(max_length=80, unique=True)

    class Meta:
        unique_together = ("product", "size", "color_name")
        ordering = ["id"]

    def __str__(self):
        return f"{self.product.name} — {self.size} / {self.color_name} (Stock: {self.stock})"


class PaymentMethodConfig(models.Model):
    code = models.CharField(max_length=30, unique=True)  # WAVE, ORANGE_MONEY, MTN_MOMO, CARD
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=255)
    instructions = models.TextField(blank=True)
    badge_label = models.CharField(max_length=80, default="Instantané")
    is_active = models.BooleanField(default=True)
    display_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["display_order", "id"]

    def __str__(self):
        status = "ACTIF" if self.is_active else "BIENTÔT DISPONIBLE"
        return f"{self.name} ({status})"


class SiteContent(models.Model):
    key = models.CharField(max_length=80, unique=True, db_index=True)
    title = models.CharField(max_length=255)
    subtitle = models.CharField(max_length=255, blank=True)
    body = models.TextField()
    cta_label = models.CharField(max_length=100, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"CMS [{self.key}] — {self.title}"


class Order(models.Model):
    class StatusChoices(models.TextChoices):
        PENDING = "PENDING", "En attente"
        CONFIRMED = "CONFIRMED", "Confirmée"
        SHIPPING = "SHIPPING", "En livraison"
        DELIVERED = "DELIVERED", "Livrée"
        CANCELLED = "CANCELLED", "Annulée"

    class PaymentStatusChoices(models.TextChoices):
        PENDING = "PENDING", "En attente"
        PAID = "PAID", "Confirmé"
        FAILED = "FAILED", "Échoué"

    order_number = models.CharField(max_length=64, unique=True, db_index=True, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="orders",
    )
    email = models.EmailField()
    full_name = models.CharField(max_length=150)
    phone = models.CharField(max_length=40)
    delivery_zone_type = models.CharField(max_length=20, default="ABIDJAN")  # ABIDJAN / INTERIEUR
    city = models.CharField(max_length=100, default="Abidjan")
    commune = models.CharField(max_length=100, default="Cocody")
    address_details = models.CharField(max_length=255)
    payment_method = models.CharField(max_length=30, default="WAVE")
    payment_reference = models.CharField(max_length=120, blank=True)
    payment_status = models.CharField(
        max_length=20,
        choices=PaymentStatusChoices.choices,
        default=PaymentStatusChoices.PAID,
    )
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.CONFIRMED,
        db_index=True,
    )
    subtotal_fcfa = models.PositiveIntegerField(default=0)
    shipping_fee_fcfa = models.PositiveIntegerField(default=2000)
    total_fcfa = models.PositiveIntegerField(default=0)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Commande ESTLE"
        verbose_name_plural = "Commandes ESTLE"
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = f"ESTLE-CI-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.order_number} — {self.full_name} ({self.total_fcfa} FCFA)"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, null=True, on_delete=models.SET_NULL)
    variant = models.ForeignKey(ProductVariant, null=True, on_delete=models.SET_NULL)
    product_name = models.CharField(max_length=200)
    product_slug = models.CharField(max_length=220, blank=True)
    image_url = models.URLField(max_length=500, blank=True)
    size = models.CharField(max_length=15)
    color_name = models.CharField(max_length=60)
    unit_price_fcfa = models.PositiveIntegerField()
    quantity = models.PositiveIntegerField(default=1)
    subtotal_fcfa = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.quantity}x {self.product_name} ({self.size} / {self.color_name})"


class Look(models.Model):
    code = models.CharField(max_length=50, default="LOOK 01", db_index=True)
    title = models.CharField(max_length=200)
    season = models.CharField(max_length=150, default="AW26 • ABIDJAN STUDIO")
    silhouette_image = models.URLField(max_length=600)
    styling_notes = models.TextField(blank=True)
    coordinates = models.CharField(max_length=150, default="5.3599° N • 4.0083° W")
    display_order = models.PositiveIntegerField(default=0, db_index=True)
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Look Éditorial"
        verbose_name_plural = "Looks Éditoriaux"
        ordering = ["display_order", "id"]

    def __str__(self):
        return f"{self.code} — {self.title}"


class LookPiece(models.Model):
    class RoleChoices(models.TextChoices):
        TOP = "TOP", "HAUT"
        BOTTOM = "BOTTOM", "BAS"
        FOOTWEAR_ACC = "FOOTWEAR / ACC", "CHAUSSURES / ACCESSOIRE"

    look = models.ForeignKey(Look, related_name="pieces", on_delete=models.CASCADE)
    role = models.CharField(
        max_length=40,
        choices=RoleChoices.choices,
        default=RoleChoices.TOP,
    )
    product = models.ForeignKey(
        Product,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="look_appearances",
    )
    fallback_name = models.CharField(max_length=200, blank=True)
    fallback_price_fcfa = models.PositiveIntegerField(default=0)
    fallback_image = models.URLField(max_length=600, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Pièce de Look"
        verbose_name_plural = "Pièces de Look"
        ordering = ["order", "id"]

    def __str__(self):
        name = self.product.name if self.product else self.fallback_name
        return f"[{self.role}] {name} ({self.look.code})"

