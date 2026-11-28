import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from store.models import Collection, Product, ProductImage, ProductVariant  # noqa: E402

acc_collection, _ = Collection.objects.get_or_create(
    slug="accessories-archive",
    defaults={
        "code": "06 — ACCESSORIES",
        "name": "ACCESSORIES ARCHIVE",
        "subtitle": "Maroquinerie, Lunettes, Chaînes & Pièces Sculpturales",
        "description": "Accessoires architecturaux ESTLE sans taille : sacs, lunettes, bijoux acier et pièces signature.",
        "editorial_quote": "Les détails définissent la silhouette.",
        "hero_image": "https://images.unsplash.com/photo-1511499767150-a48a237f0083?w=1200&auto=format&fit=crop&q=85",
        "accent_color": "#0E2920",
        "showcase_index": 6,
        "is_featured": True,
    },
)

ACCESSORIES = [
    {
        "name": "OBSIDIAN SHIELD — ARCHITECTURAL SUNGLASSES",
        "slug": "obsidian-shield-architectural-sunglasses",
        "sku": "EST-ACC-001",
        "price": 45000,
        "compare_at": 55000,
        "short_description": "Lunettes masque futuristes en acétate noir mat et verres teintés UV400.",
        "description": "Monture sculptée en acétate italien haute densité avec branches biseautées, charnières acier brossé et protection solaire intégrale UV400.",
        "fabric_specs": "Acétate poli main noir mat • Verres nylon polarisés UV400 • Étui rigide ESTLE.",
        "cut_specs": "Format universel ergonomique • Sans taille.",
        "img": "https://images.unsplash.com/photo-1511499767150-a48a237f0083?w=1000&auto=format&fit=crop&q=85",
        "color": ("Obsidian Black", "#080808"),
    },
    {
        "name": "MONOLITH SLING — LEATHER CROSSBODY",
        "slug": "monolith-sling-leather-crossbody",
        "sku": "EST-ACC-002",
        "price": 75000,
        "compare_at": 88000,
        "short_description": "Sac bandoulière structuré en cuir pleine fleur noir avec boucle métallique gunmetal.",
        "description": "Sacoche urbaine minimaliste à compartiments zippés étanches, sangle tactique réglable et doublure sergé Vert Sapin.",
        "fabric_specs": "Cuir de veau pleine fleur • Bouclerie acier gunmetal • Zip YKK Excella.",
        "cut_specs": "Dimensions 24 × 15 × 6 cm • Bandoulière réglable.",
        "img": "https://images.unsplash.com/photo-1548036328-c9fa89d128fa?w=1000&auto=format&fit=crop&q=85",
        "color": ("Obsidian Black", "#080808"),
    },
    {
        "name": "SIGIL CHAIN — HEAVY STEEL NECKLACE",
        "slug": "sigil-chain-heavy-steel-necklace",
        "sku": "EST-ACC-003",
        "price": 38000,
        "compare_at": None,
        "short_description": "Chaîne lourde à maillons architecturaux en acier inoxydable 316L brossé.",
        "description": "Collier signature forgé en acier chirurgical inoxydable résistant à l'eau et à l'oxydation, fermoir mousqueton gravé ESTLE.",
        "fabric_specs": "Acier inoxydable 316L finition argent vieilli • Hypoallergénique.",
        "cut_specs": "Longueur 52 cm • Maillons 9 mm.",
        "img": "https://images.unsplash.com/photo-1611591437281-460bfbe1220a?w=1000&auto=format&fit=crop&q=85",
        "color": ("Brushed Silver", "#A3A3A3"),
    },
    {
        "name": "NOCTURNE CAP — STRUCTURED 6-PANEL",
        "slug": "nocturne-cap-structured-6-panel",
        "sku": "EST-ACC-004",
        "price": 28000,
        "compare_at": 35000,
        "short_description": "Casquette structurée en sergé de coton lourd noir avec broderie monogramme ton-sur-ton.",
        "description": "Coupe architecturale 6 panneaux en coton épais 420 GSM, visière pré-courbée et boucle de réglage arrière en métal gravé.",
        "fabric_specs": "100% Coton sergé lourd 420 GSM • Boucle métal gravée.",
        "cut_specs": "Ajustement universel arrière • Sans taille.",
        "img": "https://images.unsplash.com/photo-1588850561407-ed78c282e89b?w=1000&auto=format&fit=crop&q=85",
        "color": ("Obsidian Black", "#080808"),
    },
    {
        "name": "ARCHIVE BELT — TACTICAL COBRA BUCKLE",
        "slug": "archive-belt-tactical-cobra-buckle",
        "sku": "EST-ACC-005",
        "price": 42000,
        "compare_at": None,
        "short_description": "Ceinture sangle nylon haute densité avec boucle tactique Cobra en aluminium anodisé.",
        "description": "Ceinture utilitaire ajustable à verrouillage rapide par boucle Cobra noire mate, extrémité renforcée en cuir grainé.",
        "fabric_specs": "Sangle nylon balistique 38 mm • Boucle aluminium anodisé.",
        "cut_specs": "Longueur 125 cm ajustable • Sans taille.",
        "img": "https://images.unsplash.com/photo-1624222247344-550fb60583dc?w=1000&auto=format&fit=crop&q=85",
        "color": ("Obsidian Black", "#080808"),
    },
    {
        "name": "PINE VAULT — CARDHOLDER LEATHER",
        "slug": "pine-vault-cardholder-leather",
        "sku": "EST-ACC-006",
        "price": 32000,
        "compare_at": 39000,
        "short_description": "Porte-cartes fin en cuir grainé Vert Sapin Profond et marquage doré ESTLE.",
        "description": "Confectionné en cuir grainé résistant avec 6 emplacements cartes et poche centrale billets, tranches teintées main.",
        "fabric_specs": "Cuir grainé Vert Sapin (#0E2920) • Marquage à chaud Or Antique.",
        "cut_specs": "Format poche ultra-fin 10 × 7,5 cm.",
        "img": "https://images.unsplash.com/photo-1627123424574-724758594e93?w=1000&auto=format&fit=crop&q=85",
        "color": ("Deep Pine", "#0E2920"),
    },
]

if Product.objects.filter(category="ACCESSORIES").exists():
    print("Des accessoires existent déjà :", Product.objects.filter(category="ACCESSORIES").count())
else:
    for item in ACCESSORIES:
        p = Product.objects.create(
            name=item["name"],
            slug=item["slug"],
            sku=item["sku"],
            collection=acc_collection,
            category="ACCESSORIES",
            price_fcfa=item["price"],
            compare_at_price_fcfa=item["compare_at"],
            short_description=item["short_description"],
            description=item["description"],
            fabric_specs=item["fabric_specs"],
            cut_specs=item["cut_specs"],
            care_instructions="Essuyer délicatement avec un chiffon sec microfibre. Ranger dans le pochon ESTLE.",
            is_featured=True,
            is_new_arrival=True,
            is_active=True,
        )
        for view_type, caption, order in [
            ("FRONT", "Vue Principale — Atelier ESTLE", 0),
            ("BACK", "Vue Perspective", 1),
            ("DETAIL", "Gros Plan Finitions & Matières", 2),
            ("LOOKBOOK", "Présentation Showroom ESTLE", 3),
        ]:
            ProductImage.objects.create(
                product=p,
                image_url=item["img"],
                view_type=view_type,
                caption=caption,
                display_order=order,
            )
        color_name, color_hex = item["color"]
        ProductVariant.objects.create(
            product=p,
            size="UNIQUE",
            color_name=color_name,
            color_hex=color_hex,
            stock=18,
            sku_variant=f"{item['sku']}-UNIQUE",
        )
    print("Accessoires créés :", Product.objects.filter(category="ACCESSORIES").count())
