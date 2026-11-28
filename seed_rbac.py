import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from accounts.models import ALL_PERMISSION_CODES, CustomUser, StaffRole  # noqa: E402

DEFAULT_ROLES = [
    {
        "code": "super_admin",
        "name": "Super Admin / Direction",
        "description": "Accès intégral à toute la Maison ESTLE, gestion équipe, rôles et sécurité.",
        "permissions": list(ALL_PERMISSION_CODES),
        "is_system": True,
    },
    {
        "code": "store_manager",
        "name": "Gérant Boutique",
        "description": "Gestion complète du catalogue, collections, looks, commandes et consultation clients.",
        "permissions": [
            "dashboard.view",
            "products.manage",
            "collections.manage",
            "looks.manage",
            "orders.view",
            "orders.manage",
            "customers.view",
            "reviews.manage",
        ],
        "is_system": False,
    },
    {
        "code": "logistics",
        "name": "Préparateur / Logistique",
        "description": "Suivi et expédition des commandes, accès aux adresses & repères GPS clients.",
        "permissions": [
            "dashboard.view",
            "orders.view",
            "orders.manage",
            "customers.view",
            "reviews.manage",
        ],
        "is_system": False,
    },
    {
        "code": "stylist",
        "name": "Éditeur / Styliste",
        "description": "Création et mise en scène des produits, collections, looks 360° et contenus CMS.",
        "permissions": [
            "dashboard.view",
            "products.manage",
            "collections.manage",
            "looks.manage",
            "settings.manage",
        ],
        "is_system": False,
    },
    {
        "code": "client",
        "name": "Client",
        "description": "Rôle attribué automatiquement à tout client inscrit sur la boutique.",
        "permissions": [],
        "is_system": True,
    },
]

roles_by_code = {}
for r in DEFAULT_ROLES:
    obj, created = StaffRole.objects.update_or_create(
        code=r["code"],
        defaults={
            "name": r["name"],
            "description": r["description"],
            "permissions": r["permissions"],
            "is_system": r["is_system"],
        },
    )
    roles_by_code[r["code"]] = obj

# Rattacher automatiquement les comptes existants
staff_updated = 0
for u in CustomUser.objects.all():
    if u.is_superuser or u.is_staff:
        u.account_type = "COLLABORATOR"
        if not u.role:
            u.role = roles_by_code["super_admin"]
        if not u.job_title:
            u.job_title = "Direction Maison ESTLE"
        u.save()
        staff_updated += 1
    else:
        u.account_type = "CLIENT"
        if not u.role:
            u.role = roles_by_code["client"]
        u.save()

print(f"RBAC seeded! Roles: {len(roles_by_code)}, Collaborators synced: {staff_updated}")
