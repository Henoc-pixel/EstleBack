import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from store.models import Collection, Product, ProductImage, ProductVariant

FOOTWEAR_ITEMS = [
    {
        "name": "AERO 01 — IVORY SCULPT",
        "slug": "aero-01-ivory-sculpt",
        "sku": "ESTLE-FW-001",
        "price_fcfa": 115000,
        "compare_at_price_fcfa": 130000,
        "short_description": "Silhouette sculptée monochrome ivoire à semelle architecturale crantée.",
        "description": "Conçue pour les volumes contemporains ESTLE, l'AERO 01 marie cuir nubuck ivoire, mesh technique respirant et semelle double densité à retour d'énergie.",
        "fabric_specs": "Cuir Nubuck Pleine Fleur • Mesh Ballistique • Semelle Vibram Custom",
        "cut_specs": "Chaussant anatomique • Semelle plateforme 4,2 cm",
        "color_name": "Ivory Bone",
        "color_hex": "#EAE6DD",
        "image": "https://images.unsplash.com/photo-1600185365483-26d7a4cc7519?w=1000&auto=format&fit=crop&q=85",
        "is_new_arrival": True,
    },
    {
        "name": "VECR 02 — ICE GLACIER",
        "slug": "vecr-02-ice-glacier",
        "sku": "ESTLE-FW-002",
        "price_fcfa": 105000,
        "compare_at_price_fcfa": None,
        "short_description": "Runner minimaliste bleu glacier à empeigne tissée sans couture.",
        "description": "Lignes tendues et légèreté absolue : la VECR 02 associe tricot technique haute ténacité bleu glacier et amorti réactif ultra-fin.",
        "fabric_specs": "Knit Technique Sans Couture • Semelle EVA Supercritique",
        "cut_specs": "Profil bas aérodynamique • Poids plume 265g",
        "color_name": "Ice Glacier",
        "color_hex": "#CFE4E8",
        "image": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=1000&auto=format&fit=crop&q=85",
        "is_new_arrival": True,
    },
    {
        "name": "DUNE 03 — SAND RUNNER",
        "slug": "dune-03-sand-runner",
        "sku": "ESTLE-FW-003",
        "price_fcfa": 120000,
        "compare_at_price_fcfa": 135000,
        "short_description": "Daim sable et nylon ripstop inspirés des dunes minérales.",
        "description": "Superposition de daim brossé sable, empiècements réfléchissants 3M et semelle gomme naturelle pour une adhérence urbaine irréprochable.",
        "fabric_specs": "Daim Italien Brossé • Nylon Ripstop • Semelle Gomme",
        "cut_specs": "Coupe Mid-Runner • Maintien talon renforcé",
        "color_name": "Sand Dune",
        "color_hex": "#D5C3A5",
        "image": "https://images.unsplash.com/photo-1551107696-a4b0c5a0d9a2?w=1000&auto=format&fit=crop&q=85",
        "is_new_arrival": False,
    },
    {
        "name": "MONO 04 — CONCRETE GREY",
        "slug": "mono-04-concrete-grey",
        "sku": "ESTLE-FW-004",
        "price_fcfa": 110000,
        "compare_at_price_fcfa": None,
        "short_description": "Architecture gris béton et détails métalliques argent brossé.",
        "description": "Un hommage brutaliste au béton ciré : empiècements superposés gris minéral, lacets ronds techniques et talon stabilisateur en TPU.",
        "fabric_specs": "Cuir Suédé Gris Minéral • TPU Moulé • Doublure Néoprène",
        "cut_specs": "Volume structuré • Soutien voûte plantaire",
        "color_name": "Concrete Grey",
        "color_hex": "#9A9B9F",
        "image": "https://images.unsplash.com/photo-1539185441755-769473a23570?w=1000&auto=format&fit=crop&q=85",
        "is_new_arrival": False,
    },
    {
        "name": "VAPOR 05 — MIST CLOUD",
        "slug": "vapor-05-mist-cloud",
        "sku": "ESTLE-FW-005",
        "price_fcfa": 128000,
        "compare_at_price_fcfa": None,
        "short_description": "Semelle bulle sculptée et tige multi-couches brume argentée.",
        "description": "Équilibre futuriste entre transparence et maintien : la VAPOR 05 combine mesh argenté, renforts thermosoudés et amorti pneumatique visible.",
        "fabric_specs": "Mesh Technique Argent • Renforts Thermosoudés • Semelle Air",
        "cut_specs": "Coupe Chunky Architecturale • Confort longue durée",
        "color_name": "Mist Silver",
        "color_hex": "#D8DEE2",
        "image": "https://images.unsplash.com/photo-1606107557195-0e29a4b5b4aa?w=1000&auto=format&fit=crop&q=85",
        "is_new_arrival": True,
    },
    {
        "name": "RIFT 06 — VOLT TRAIL",
        "slug": "rift-06-volt-trail",
        "sku": "ESTLE-FW-006",
        "price_fcfa": 135000,
        "compare_at_price_fcfa": 150000,
        "short_description": "Conçue pour les terrains exigeants et les silhouettes pointues.",
        "description": "Semelle cramponnée tout-terrain, tige ripstop kaki olive soulignée de surpiqûres jaune volt et laçage rapide à bloqueur métallique.",
        "fabric_specs": "Ripstop Déperlant • Crampons Haute Traction • Inserts Volt",
        "cut_specs": "Maintien Trail Tactique • Pare-pierres avant",
        "color_name": "Olive Volt",
        "color_hex": "#7D8B4E",
        "image": "https://images.unsplash.com/photo-1595950653106-6c9ebd614d3a?w=1000&auto=format&fit=crop&q=85",
        "is_new_arrival": True,
    },
    {
        "name": "COURT 07 — GUM ARCHIVE",
        "slug": "court-07-gum-archive",
        "sku": "ESTLE-FW-007",
        "price_fcfa": 95000,
        "compare_at_price_fcfa": None,
        "short_description": "Cuir blanc craie minimaliste monté sur semelle gomme miel.",
        "description": "Réinterprétation épurée de la sneaker court classique : cuir pleine fleur blanc craie, doublure cuir souple et semelle gomme naturelle.",
        "fabric_specs": "100% Cuir Pleine Fleur • Semelle Gomme Naturelle Cousue",
        "cut_specs": "Silhouette basse intemporelle • Finition atelier",
        "color_name": "Chalk Gum",
        "color_hex": "#F2EFE9",
        "image": "https://images.unsplash.com/photo-1525966222134-fcfa99b8ae77?w=1000&auto=format&fit=crop&q=85",
        "is_new_arrival": False,
    },
    {
        "name": "MONOLITH 08 — OCHRE BOOT",
        "slug": "monolith-08-ochre-boot",
        "sku": "ESTLE-FW-008",
        "price_fcfa": 148000,
        "compare_at_price_fcfa": 165000,
        "short_description": "Bottine tactique en nubuck ocre doré à col matelassé.",
        "description": "Allure monumentale et robustesse d'atelier : nubuck hydrofuge ocre doré, œillets hexagonaux en laiton brossé et semelle crantée lourde.",
        "fabric_specs": "Nubuck Hydrofuge Ocre • Œillets Laiton • Semelle Crantée",
        "cut_specs": "Tige montante cheville • Col cuir matelassé",
        "color_name": "Ochre Gold",
        "color_hex": "#C89D54",
        "image": "https://images.unsplash.com/photo-1608231387042-66d1773070a5?w=1000&auto=format&fit=crop&q=85",
        "is_new_arrival": False,
    },
    {
        "name": "PULSE 09 — CRIMSON VELOCITY",
        "slug": "pulse-09-crimson-velocity",
        "sku": "ESTLE-FW-009",
        "price_fcfa": 112000,
        "compare_at_price_fcfa": None,
        "short_description": "Éclat rouge carmin sur semelle blanche sculptée haute réponse.",
        "description": "Pièce statement de la ligne Footwear : daim rouge carmin saturé, languette ergonomique fine et semelle intermédiaire blanche ultra-réactive.",
        "fabric_specs": "Daim Carmin Premium • Mesh Respirant • Semelle Réactive",
        "cut_specs": "Coupe profilée dynamique • Maintien médio-pied",
        "color_name": "Crimson Red",
        "color_hex": "#C82333",
        "image": "https://images.unsplash.com/photo-1549298916-b41d501d3772?w=1000&auto=format&fit=crop&q=85",
        "is_new_arrival": True,
    },
    {
        "name": "VERGE 10 — MINT HERITAGE",
        "slug": "verge-10-mint-heritage",
        "sku": "ESTLE-FW-010",
        "price_fcfa": 132000,
        "compare_at_price_fcfa": None,
        "short_description": "Daim vert menthe pastel, mesh technique et détails rétro-futuristes.",
        "description": "Édition collector VERGE 10 : assemblage multi-matières en daim vert sauge/menthe, tirant arrière technique et semelle bicolore crantée.",
        "fabric_specs": "Daim Sauge & Menthe • Mesh Perforé • Semelle Double Densité",
        "cut_specs": "Coupe rétro-runner architecturale • Édition numérotée",
        "color_name": "Sage Mint",
        "color_hex": "#9CC5B8",
        "image": "https://images.unsplash.com/photo-1584735935682-2f2b69dff9d2?w=1000&auto=format&fit=crop&q=85",
        "is_new_arrival": True,
    },
]

EU_SIZES = ["EU 39", "EU 40", "EU 41", "EU 42", "EU 43", "EU 44", "EU 45"]


def run():
    col, _ = Collection.objects.update_or_create(
        slug="footwear-archive",
        defaults={
            "code": "05 — FOOTWEAR",
            "name": "FOOTWEAR ARCHIVE",
            "subtitle": "Form, lit from within.",
            "description": "Sneakers architecturales, runners techniques et bottines sculpturales conçues pour compléter les silhouettes ESTLE.",
            "editorial_quote": "Form, lit from within.",
            "hero_image": FOOTWEAR_ITEMS[0]["image"],
            "secondary_image": FOOTWEAR_ITEMS[5]["image"],
            "accent_color": "#FF6A00",
            "showcase_index": 5,
            "shader_type": "kinetic",
            "is_featured": True,
        },
    )

    created_count = 0
    for item in FOOTWEAR_ITEMS:
        prod, created = Product.objects.update_or_create(
            slug=item["slug"],
            defaults={
                "collection": col,
                "category": Product.CategoryChoices.FOOTWEAR,
                "name": item["name"],
                "sku": item["sku"],
                "price_fcfa": item["price_fcfa"],
                "compare_at_price_fcfa": item["compare_at_price_fcfa"],
                "short_description": item["short_description"],
                "description": item["description"],
                "fabric_specs": item["fabric_specs"],
                "cut_specs": item["cut_specs"],
                "care_instructions": "Nettoyage à sec avec brosse douce • Imperméabilisant recommandé",
                "shader_preset": "kinetic",
                "is_new_arrival": item["is_new_arrival"],
                "is_featured": True,
                "is_active": True,
            },
        )
        if created:
            created_count += 1

        prod.images.all().delete()
        ProductImage.objects.create(
            product=prod,
            image_url=item["image"],
            view_type="FRONT",
            caption=f"{item['name']} — Profil Studio",
            display_order=0,
        )
        ProductImage.objects.create(
            product=prod,
            image_url=item["image"],
            view_type="DETAIL",
            caption=f"{item['name']} — Détail Semelle & Matières",
            display_order=1,
        )

        for sz in EU_SIZES:
            sku_v = f"{item['sku']}-{sz.replace(' ', '')}"
            ProductVariant.objects.update_or_create(
                sku_variant=sku_v,
                defaults={
                    "product": prod,
                    "size": sz,
                    "color_name": item["color_name"],
                    "color_hex": item["color_hex"],
                    "stock": 8,
                },
            )

    total_fw = Product.objects.filter(category=Product.CategoryChoices.FOOTWEAR).count()
    print(f"Footwear seeding complete! Created: {created_count}, Total FOOTWEAR products: {total_fw}")


if __name__ == "__main__":
    run()
