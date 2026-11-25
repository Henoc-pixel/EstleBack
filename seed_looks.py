import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from store.models import Look, LookPiece, Product

BASE_7_LOOKS = [
    {
        "code_prefix": "LOOK 01",
        "title": "OBSIDIAN DRAPERY",
        "season": "AW26 • ABIDJAN STUDIO",
        "silhouette_image": "/looks/look-01.png",
        "styling_notes": "Superposition architecturale en molleton 540 GSM avec chest bag sanglé et pantalon cargo multi-œillets.",
        "coordinates": "5.3599° N • 4.0083° W",
        "pieces": [
            {
                "role": "TOP",
                "product_slug": "hoodie-architectural-void-540",
                "fallback_name": "HOODIE ARCHITECTURAL 'VOID 540'",
                "fallback_price_fcfa": 85000,
                "fallback_image": "https://images.unsplash.com/photo-1556821840-3a63f95609a7?w=800&auto=format&fit=crop&q=80",
            },
            {
                "role": "BOTTOM",
                "product_slug": "pantalon-cargo-obsidian",
                "fallback_name": "PANTALON CARGO STRUCTURE 'OBSIDIAN'",
                "fallback_price_fcfa": 95000,
                "fallback_image": "https://images.unsplash.com/photo-1624378439575-d8705ad7ae80?w=800&auto=format&fit=crop&q=80",
            },
            {
                "role": "FOOTWEAR / ACC",
                "product_slug": "sac-crossbody-cuir-mineral",
                "fallback_name": "SAC CROSSBODY CUIR 'MINÉRAL'",
                "fallback_price_fcfa": 65000,
                "fallback_image": "https://images.unsplash.com/photo-1548036328-c9fa89d128fa?w=800&auto=format&fit=crop&q=80",
            },
        ],
    },
    {
        "code_prefix": "LOOK 02",
        "title": "POLAR SHERPA & DEEP PINE",
        "season": "COLLECTION CAPSULE • VERT SAPIN",
        "silhouette_image": "/looks/look-02.png",
        "styling_notes": "Veste hybride en polaire sherpa noire et nylon technique, bonnet en maille côtelée et cargo vert sapin.",
        "coordinates": "ATELIER COCODY • ABIDJAN",
        "pieces": [
            {
                "role": "TOP",
                "product_slug": "veste-tailoring-sapin-profond",
                "fallback_name": "VESTE SHERPA FLEECE 'ESTLE'",
                "fallback_price_fcfa": 145000,
                "fallback_image": "https://images.unsplash.com/photo-1591047139829-d91aecb6caea?w=800&auto=format&fit=crop&q=80",
            },
            {
                "role": "BOTTOM",
                "product_slug": "pantalon-plisse-vert-sapin",
                "fallback_name": "CARGO TECHNIQUE VERT SAPIN",
                "fallback_price_fcfa": 98000,
                "fallback_image": "https://images.unsplash.com/photo-1517445312882-bc9910d016b7?w=800&auto=format&fit=crop&q=80",
            },
            {
                "role": "FOOTWEAR / ACC",
                "product_slug": "sac-crossbody-cuir-mineral",
                "fallback_name": "SACOCHE CROSSBODY BI-TON PINE",
                "fallback_price_fcfa": 55000,
                "fallback_image": "https://images.unsplash.com/photo-1548036328-c9fa89d128fa?w=800&auto=format&fit=crop&q=80",
            },
        ],
    },
    {
        "code_prefix": "LOOK 03",
        "title": "COLOR-BLOCK PUFFER DUNE",
        "season": "HIVER URBAIN • ÉDITION LIMITÉE",
        "silhouette_image": "/looks/look-03.png",
        "styling_notes": "Doudoune matelassée tri-tons (marine, brique et olive) avec broderie lettrage ESTLE et pantalon cargo sable.",
        "coordinates": "ZONE 4 • ABIDJAN STUDIO",
        "pieces": [
            {
                "role": "TOP",
                "product_slug": "bomber-sculptural-eclipse-ma1",
                "fallback_name": "DOUDOUNE TRI-TON PUFFER 'ESTLE'",
                "fallback_price_fcfa": 155000,
                "fallback_image": "https://images.unsplash.com/photo-1544441893-675973e31985?w=800&auto=format&fit=crop&q=80",
            },
            {
                "role": "BOTTOM",
                "product_slug": "pantalon-tailoring-ivoire",
                "fallback_name": "PANTALON CARGO OVERSIZE SABLE",
                "fallback_price_fcfa": 92000,
                "fallback_image": "https://images.unsplash.com/photo-1624378439575-d8705ad7ae80?w=800&auto=format&fit=crop&q=80",
            },
            {
                "role": "FOOTWEAR / ACC",
                "product_slug": "baskets-basses-architecturales",
                "fallback_name": "SNEAKERS TRAIL RUNNER ESTLE",
                "fallback_price_fcfa": 115000,
                "fallback_image": "https://images.unsplash.com/photo-1549298916-b41d501d3772?w=800&auto=format&fit=crop&q=80",
            },
        ],
    },
    {
        "code_prefix": "LOOK 04",
        "title": "COLLEGIATE VARSITY 1996",
        "season": "ARCHIVES ESTLE • HERITAGE",
        "silhouette_image": "/looks/look-04.png",
        "styling_notes": "Teddy universitaire 'ESTLE EST. 1996' en nylon vert et jaune, sweat à capuche chiné et velours côtelé marron.",
        "coordinates": "5.3599° N • 4.0083° W",
        "pieces": [
            {
                "role": "TOP",
                "product_slug": "trench-architectural-olive",
                "fallback_name": "VESTE VARSITY 'ESTLE 1996'",
                "fallback_price_fcfa": 138000,
                "fallback_image": "https://images.unsplash.com/photo-1551028719-00167b16eac5?w=800&auto=format&fit=crop&q=80",
            },
            {
                "role": "BOTTOM",
                "product_slug": "pantalon-cargo-obsidian",
                "fallback_name": "PANTALON VELOURS CÔTELÉ MOKA",
                "fallback_price_fcfa": 88000,
                "fallback_image": "https://images.unsplash.com/photo-1594633312681-425c7b97ccd1?w=800&auto=format&fit=crop&q=80",
            },
            {
                "role": "FOOTWEAR / ACC",
                "product_slug": "baskets-basses-architecturales",
                "fallback_name": "SNEAKERS SKATE VERT & BLANC",
                "fallback_price_fcfa": 98000,
                "fallback_image": "https://images.unsplash.com/photo-1549298916-b41d501d3772?w=800&auto=format&fit=crop&q=80",
            },
        ],
    },
    {
        "code_prefix": "LOOK 05",
        "title": "TACTICAL MATRIX RIG",
        "season": "TECHWEAR NOIR • ESTLE",
        "silhouette_image": "/looks/look-05.png",
        "styling_notes": "Volume utilitaire furtif : hoodie noir lourd, harnais chest-rig olive et cargo à sangles multiples.",
        "coordinates": "FLAGSHIP ABIDJAN • DROP 05",
        "pieces": [
            {
                "role": "TOP",
                "product_slug": "hoodie-architectural-void-540",
                "fallback_name": "HOODIE MATTE BLACK & HARNAIS",
                "fallback_price_fcfa": 92000,
                "fallback_image": "https://images.unsplash.com/photo-1556821840-3a63f95609a7?w=800&auto=format&fit=crop&q=80",
            },
            {
                "role": "BOTTOM",
                "product_slug": "pantalon-cargo-monolith",
                "fallback_name": "CARGO TACTIQUE SANGLES MULTIPLES",
                "fallback_price_fcfa": 96000,
                "fallback_image": "https://images.unsplash.com/photo-1624378439575-d8705ad7ae80?w=800&auto=format&fit=crop&q=80",
            },
            {
                "role": "FOOTWEAR / ACC",
                "product_slug": "boots-chelsea-cuir-vert-sombre",
                "fallback_name": "BOTTES MILITAIRES TACTICAL COMBAT",
                "fallback_price_fcfa": 128000,
                "fallback_image": "https://images.unsplash.com/photo-1533867617858-e7b97e060509?w=800&auto=format&fit=crop&q=80",
            },
        ],
    },
    {
        "code_prefix": "LOOK 06",
        "title": "GOTHIC MONOLITH TRENCH",
        "season": "HAUTE COUTURE GOTHIC • ESTLE",
        "silhouette_image": "/looks/look-06.png",
        "styling_notes": "Manteau long trench noir épuré sur hoodie Gothic Estle avec parure de chaînes acier et bottes à plaques de métal.",
        "coordinates": "5.3599° N • 4.0083° W",
        "pieces": [
            {
                "role": "TOP",
                "product_slug": "trench-architectural-olive",
                "fallback_name": "MANTEAU LONG MONOLITH NOIR",
                "fallback_price_fcfa": 175000,
                "fallback_image": "https://images.unsplash.com/photo-1544441893-675973e31985?w=800&auto=format&fit=crop&q=80",
            },
            {
                "role": "BOTTOM",
                "product_slug": "pantalon-cargo-obsidian",
                "fallback_name": "PANTALON GOTHIC CARGO HARNESS",
                "fallback_price_fcfa": 105000,
                "fallback_image": "https://images.unsplash.com/photo-1624378439575-d8705ad7ae80?w=800&auto=format&fit=crop&q=80",
            },
            {
                "role": "FOOTWEAR / ACC",
                "product_slug": "derbies-cuir-noir-semelle-sculptee",
                "fallback_name": "BOTTES CUIRASSE BUCKLE COMBAT",
                "fallback_price_fcfa": 145000,
                "fallback_image": "https://images.unsplash.com/photo-1533867617858-e7b97e060509?w=800&auto=format&fit=crop&q=80",
            },
        ],
    },
    {
        "code_prefix": "LOOK 07",
        "title": "CYBER UTILITY VEST",
        "season": "STREETWEAR TACTIQUE • AW26",
        "silhouette_image": "/looks/look-07.png",
        "styling_notes": "Gilet tactique modulaire, hoodie Gothic brodé, jean cargo délavé à anneaux et mousquetons de suspension.",
        "coordinates": "ATELIER COCODY • ABIDJAN",
        "pieces": [
            {
                "role": "TOP",
                "product_slug": "hoodie-architectural-void-540",
                "fallback_name": "GILET TACTIQUE MULTI-POCHES ESTLE",
                "fallback_price_fcfa": 110000,
                "fallback_image": "https://images.unsplash.com/photo-1556821840-3a63f95609a7?w=800&auto=format&fit=crop&q=80",
            },
            {
                "role": "BOTTOM",
                "product_slug": "pantalon-cargo-monolith",
                "fallback_name": "JEAN CARGO NOIR DESTROY & SANGLES",
                "fallback_price_fcfa": 98000,
                "fallback_image": "https://images.unsplash.com/photo-1624378439575-d8705ad7ae80?w=800&auto=format&fit=crop&q=80",
            },
            {
                "role": "FOOTWEAR / ACC",
                "product_slug": "sac-crossbody-cuir-mineral",
                "fallback_name": "COLLIER CHAÎNE CADENAS & SACOCHE",
                "fallback_price_fcfa": 68000,
                "fallback_image": "https://images.unsplash.com/photo-1548036328-c9fa89d128fa?w=800&auto=format&fit=crop&q=80",
            },
        ],
    },
]

# Construire les 14 looks : 1 à 7, puis les duplicatas 8 à 14 séparés
ALL_14_LOOKS = []

# Première série (LOOK 01 à LOOK 07)
for idx, item in enumerate(BASE_7_LOOKS):
    ALL_14_LOOKS.append({
        "code": f"LOOK {idx + 1:02d}",
        "title": item["title"],
        "season": item["season"],
        "silhouette_image": item["silhouette_image"],
        "styling_notes": item["styling_notes"],
        "coordinates": item["coordinates"],
        "display_order": idx,
        "pieces": item["pieces"],
    })

# Deuxième série : Duplicatas séparés (LOOK 08 à LOOK 14)
for idx, item in enumerate(BASE_7_LOOKS):
    ALL_14_LOOKS.append({
        "code": f"LOOK {idx + 8:02d}",
        "title": f"{item['title']} (VARIATION)",
        "season": item["season"],
        "silhouette_image": item["silhouette_image"],
        "styling_notes": f"Seconde perspective éditoriale : {item['styling_notes']}",
        "coordinates": item["coordinates"],
        "display_order": idx + 7,
        "pieces": item["pieces"],
    })

print("Seeding 14 looks (7 transparent models + 7 separated duplicates)...")
# Supprimer les anciens looks pour recréer la suite propre
Look.objects.all().delete()

for idx, data in enumerate(ALL_14_LOOKS):
    look = Look.objects.create(
        code=data["code"],
        title=data["title"],
        season=data["season"],
        silhouette_image=data["silhouette_image"],
        styling_notes=data["styling_notes"],
        coordinates=data["coordinates"],
        display_order=data["display_order"],
        is_active=True,
    )
    for p_idx, p_spec in enumerate(data["pieces"]):
        prod = Product.objects.filter(slug=p_spec["product_slug"]).first()
        LookPiece.objects.create(
            look=look,
            role=p_spec["role"],
            product=prod,
            fallback_name=p_spec["fallback_name"],
            fallback_price_fcfa=p_spec["fallback_price_fcfa"],
            fallback_image=p_spec["fallback_image"],
            order=p_idx,
        )

print(f"Success! Total looks created: {Look.objects.count()}, Total pieces: {LookPiece.objects.count()}")
