from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


ALL_PERMISSIONS = [
    {"code": "dashboard.view", "label": "Tableau de bord & KPIs", "group": "Général"},
    {"code": "products.manage", "label": "Gérer les produits, prix & stocks", "group": "Catalogue"},
    {"code": "collections.manage", "label": "Gérer les collections & vitrines", "group": "Catalogue"},
    {"code": "looks.manage", "label": "Gérer les Looks & Silhouettes 360°", "group": "Catalogue"},
    {"code": "orders.view", "label": "Consulter les commandes", "group": "Commandes"},
    {"code": "orders.manage", "label": "Modifier le statut & expédier les commandes", "group": "Commandes"},
    {"code": "customers.view", "label": "Consulter la liste & fiches clients", "group": "Clients"},
    {"code": "customers.manage", "label": "Activer / suspendre un compte client", "group": "Clients"},
    {"code": "reviews.manage", "label": "Modérer & valider les avis clients", "group": "Clients"},
    {"code": "team.manage", "label": "Créer & gérer les collaborateurs", "group": "Équipe & Accès"},
    {"code": "roles.manage", "label": "Créer & modifier les rôles et permissions", "group": "Équipe & Accès"},
    {"code": "settings.manage", "label": "Gérer les paiements & textes CMS", "group": "Configuration"},
    {"code": "audit.view", "label": "Consulter le journal d'audit", "group": "Sécurité"},
]

ALL_PERMISSION_CODES = [p["code"] for p in ALL_PERMISSIONS]


class StaffRole(models.Model):
    code = models.SlugField(max_length=60, unique=True, db_index=True)
    name = models.CharField(max_length=120)
    description = models.CharField(max_length=255, blank=True)
    permissions = models.JSONField(default=list, blank=True)
    is_system = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Rôle"
        verbose_name_plural = "Rôles"
        ordering = ["id"]

    def __str__(self):
        return f"{self.name} ({self.code})"


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("L'adresse e-mail est obligatoire.")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("account_type", "COLLABORATOR")

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Le superutilisateur doit avoir is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Le superutilisateur doit avoir is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    class AccountTypeChoices(models.TextChoices):
        CLIENT = "CLIENT", "Client"
        COLLABORATOR = "COLLABORATOR", "Collaborateur"

    email = models.EmailField(unique=True, db_index=True, max_length=255)
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    phone_number = models.CharField(max_length=40, blank=True)
    default_city = models.CharField(max_length=100, default="Abidjan", blank=True)
    default_commune = models.CharField(max_length=100, default="Cocody", blank=True)
    default_address = models.CharField(max_length=255, blank=True)

    # RBAC & Type de compte (Client vs Collaborateur)
    account_type = models.CharField(
        max_length=20,
        choices=AccountTypeChoices.choices,
        default=AccountTypeChoices.CLIENT,
        db_index=True,
    )
    role = models.ForeignKey(
        StaffRole,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="users",
    )
    extra_permissions = models.JSONField(default=list, blank=True)
    job_title = models.CharField(max_length=120, blank=True)

    # Sécurité 2FA (TOTP)
    is_2fa_enabled = models.BooleanField(default=False)
    totp_secret = models.CharField(max_length=64, blank=True)
    backup_codes = models.JSONField(default=list, blank=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = "Utilisateur"
        verbose_name_plural = "Utilisateurs"
        ordering = ["-date_joined"]

    def __str__(self):
        return self.email

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip() or self.email

    @property
    def effective_permissions(self) -> list[str]:
        if self.is_superuser:
            return list(ALL_PERMISSION_CODES)
        perms = set()
        if self.role and isinstance(self.role.permissions, list):
            if "*" in self.role.permissions:
                return list(ALL_PERMISSION_CODES)
            perms.update(self.role.permissions)
        if isinstance(self.extra_permissions, list):
            perms.update(self.extra_permissions)
        return sorted(perms)

    def has_estle_perm(self, perm_code: str) -> bool:
        if self.is_superuser:
            return True
        if self.account_type != self.AccountTypeChoices.COLLABORATOR and not self.is_staff:
            return False
        return perm_code in self.effective_permissions


class CustomerAddress(models.Model):
    user = models.ForeignKey(
        CustomUser,
        related_name="addresses",
        on_delete=models.CASCADE,
    )
    label = models.CharField(max_length=60, default="Maison")
    recipient_name = models.CharField(max_length=150, blank=True)
    phone = models.CharField(max_length=40, blank=True)
    delivery_zone_type = models.CharField(max_length=20, default="ABIDJAN")
    city = models.CharField(max_length=100, default="Abidjan")
    commune = models.CharField(max_length=100, default="Cocody")
    address_details = models.CharField(max_length=255)
    landmark = models.CharField(max_length=255, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Adresse de livraison"
        verbose_name_plural = "Adresses de livraison"
        ordering = ["-is_default", "-created_at"]

    def __str__(self):
        return f"{self.user.email} — {self.label} ({self.commune})"


class AuditLog(models.Model):
    actor = models.ForeignKey(
        CustomUser,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="audit_logs",
    )
    actor_email = models.CharField(max_length=255, blank=True)
    action = models.CharField(max_length=100, db_index=True)
    target_type = models.CharField(max_length=60, blank=True)
    target_id = models.CharField(max_length=64, blank=True)
    summary = models.CharField(max_length=300)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = "Journal d'audit"
        verbose_name_plural = "Journal d'audit"
        ordering = ["-created_at"]

    def __str__(self):
        return f"[{self.action}] {self.actor_email}: {self.summary}"


class Notification(models.Model):
    class AudienceChoices(models.TextChoices):
        CLIENT = "CLIENT", "Client"
        ADMIN = "ADMIN", "Administration"

    class CategoryChoices(models.TextChoices):
        ORDER = "ORDER", "Commande"
        REVIEW = "REVIEW", "Avis & Note"
        CUSTOMER = "CUSTOMER", "Client"
        SECURITY = "SECURITY", "Sécurité"
        SYSTEM = "SYSTEM", "Système"

    audience = models.CharField(
        max_length=16,
        choices=AudienceChoices.choices,
        default=AudienceChoices.CLIENT,
        db_index=True,
    )
    recipient = models.ForeignKey(
        CustomUser,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    required_permission = models.CharField(max_length=80, blank=True, db_index=True)
    category = models.CharField(
        max_length=20,
        choices=CategoryChoices.choices,
        default=CategoryChoices.SYSTEM,
        db_index=True,
    )
    title = models.CharField(max_length=180)
    message = models.TextField()
    link = models.CharField(max_length=255, blank=True)
    is_read = models.BooleanField(default=False, db_index=True)
    read_by_ids = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"
        ordering = ["-created_at"]

    def is_read_for(self, user_id: int) -> bool:
        if self.recipient_id is not None:
            return bool(self.is_read)
        return user_id in (self.read_by_ids or [])

    def __str__(self):
        return f"[{self.audience}/{self.category}] {self.title}"
