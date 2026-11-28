import os
import shutil
from pathlib import Path
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from store.models import Collection, Product, ProductImage, ProductVariant  # noqa: E402

UPLOAD_DIR = Path(
    r"C:\Users\elloh\.gemini\antigravity\brain\813dc14b-84df-42f4-ac41-3ea0b3d9f1a2\.user_uploaded"
)
PUBLIC_FOOTWEAR_DIR = Path(
    r"c:\Users\elloh\Documents\ESPACE DE TRAVAIL\ESTLE\frontestle\public\images\footwear"
)
PUBLIC_FOOTWEAR_DIR.mkdir(parents=True, exist_ok=True)

SHOES = [
    {
        "src": "media_1795670012959_a9f31a89.webp",
        "dest": "estle-fw-01-obsidian-chain-boot.webp",
        "name": "OBSIDIAN CHAIN — PLATFORM BOOT",
        "slug": "obsidian-chain-platform-boot",
        "sku": "EST-FW-001",
        "price": 135000,
        "compare_at": 155000,
        "short_description": "Botte haute gothique à plateforme crantée, harnais clouté et chaînes métalliques amovibles.",
        "description": "Botte montante architecturale en cuir noir mat avec zip latéral intégral, double sangles à pointes et chaînes en acier brossé drapé sur la tige et la plateforme.",
        "fabric_specs": "Cuir pleine fleur noir mat, quincaillerie acier brossé, semelle caoutchouc vulcanisé 7 cm.",
        "cut_specs": "Tige mi-mollet structurée, fermeture zip + laçage 10 œillets, maintien cheville renforcé.",
        "is_featured": True,
        "is_new_arrival": True,
    },
    {
        "src": "media_1795670012964_15165b46.webp",
        "dest": "estle-fw-02-pentagram-patent-sneaker.webp",
        "name": "NOCTURNE HARNESS — PATENT PLATFORM",
        "slug": "nocturne-harness-patent-platform",
        "sku": "EST-FW-002",
        "price": 115000,
        "compare_at": 130000,
        "short_description": "Sneaker plateforme vernie noire avec harnais pentagramme argenté et semelle sculptée.",
        "description": "Silhouette basse-montante mêlant cuir grainé et empiècements vernis miroir, rehaussée d'un anneau pentagramme en métal massif, chaînes latérales et semelle chunky haute densité.",
        "fabric_specs": "Cuir grainé & cuir verni noir profond, boucle pentagramme alliage acier, semelle EVA crantée.",
        "cut_specs": "Coupe Chunky Platform 6 cm, col rembourré confort longue durée.",
        "is_featured": True,
        "is_new_arrival": True,
    },
    {
        "src": "media_1795670013007_60d686d4.webp",
        "dest": "estle-fw-03-arachne-velvet-creeper.webp",
        "name": "ARACHNE VELVET — WEB CREEPER",
        "slug": "arachne-velvet-web-creeper",
        "sku": "EST-FW-003",
        "price": 95000,
        "compare_at": None,
        "short_description": "Creeper plateforme en velours noir brodé de toiles d'araignées argentées.",
        "description": "Derby creeper iconique à semelle striée épaisse, associant velours noir profond, contreforts en cuir lisse, anneaux D-ring métalliques et broderies fil argent haute précision.",
        "fabric_specs": "Velours ras noir, cuir lisse végétal, broderie fil métallisé argent, semelle crêpe striée.",
        "cut_specs": "Forme Creeper classique à bout rond, semelle plateforme 5 cm.",
        "is_featured": True,
        "is_new_arrival": False,
    },
    {
        "src": "media_1795670013009_7f40b5fd.webp",
        "dest": "estle-fw-04-cathedral-gothic-boot.webp",
        "name": "CATHÉDRALE — SCULPTED HEEL BOOT",
        "slug": "cathedrale-sculpted-heel-boot",
        "sku": "EST-FW-004",
        "price": 145000,
        "compare_at": 165000,
        "short_description": "Botte haute en cuir vieilli avec talon cathédrale sculpté et bout métal gravé baroque.",
        "description": "Pièce maîtresse de l'archive ESTLE : talon bloc ciselé en ogives gothiques, coque avant métallique gravée d'arabesques baroques et boucles ornementales en étain vieilli.",
        "fabric_specs": "Cuir de veau pleine fleur, talon & embout métal patiné gravé, semelle crantée antidérapante.",
        "cut_specs": "Botte haute 12 œillets, talon bloc architectural 6,5 cm.",
        "is_featured": True,
        "is_new_arrival": True,
    },
    {
        "src": "media_1795670013011_60816d88.webp",
        "dest": "estle-fw-05-valkyrie-armor-boot.webp",
        "name": "VALKYRIE ARMOR — HEAVY COMBAT BOOT",
        "slug": "valkyrie-armor-heavy-combat-boot",
        "sku": "EST-FW-005",
        "price": 140000,
        "compare_at": 160000,
        "short_description": "Botte combat massive à clous pyramides, chaînes drapé et renforts métalliques de semelle.",
        "description": "Construction lourde d'inspiration industrielle : triples sangles à clous pyramides, chaînes en acier gunmetal, zip latéral et semelle tank renforcée de plaques métalliques.",
        "fabric_specs": "Cuir robuste grain naturel, clous et plaques acier gunmetal, semelle tank 7,5 cm.",
        "cut_specs": "Maintien intégral cheville & mollet, chaussant ergonomique.",
        "is_featured": True,
        "is_new_arrival": True,
    },
    {
        "src": "media_1795670013005_af60abdd.webp",
        "dest": "estle-fw-06-cyber-crimson-tactical.webp",
        "name": "KINETIC CRIMSON — TACTICAL RUNNER",
        "slug": "kinetic-crimson-tactical-runner",
        "sku": "EST-FW-006",
        "price": 105000,
        "compare_at": 120000,
        "short_description": "Sneaker techwear noire à liserés cramoisis et doubles boucles tactiques Cobra.",
        "description": "Sneaker d'assaut urbain en mesh balistique et empiècements synthétiques techniques, équipée de sangles réglables à boucles tactiques rapides et semelle trail haute accroche.",
        "fabric_specs": "Mesh balistique respirant, renforts TPU, boucles tactiques métal mat, semelle trail.",
        "cut_specs": "Coupe basse dynamique, laçage rapide + double verrouillage sangle.",
        "is_featured": True,
        "is_new_arrival": True,
    },
    {
        "src": "media_1795670013014_af0ca399.webp",
        "dest": "estle-fw-07-cathedral-ankle-boot.webp",
        "name": "CATHÉDRALE LOW — DOUBLE BUCKLE",
        "slug": "cathedrale-low-double-buckle",
        "sku": "EST-FW-007",
        "price": 125000,
        "compare_at": None,
        "short_description": "Bottine basse en cuir noir à talon cathédrale sculpté, doubles boucles cloutées et bout acier.",
        "description": "Déclinaison cheville de la botte Cathédrale : double brides cloutées à boucles gravées, bout acier brossé ciselé et semelle ornée de frises gothiques en relief.",
        "fabric_specs": "Cuir noir pleine fleur, embout acier gravé, talon sculpté haute résistance.",
        "cut_specs": "Hauteur cheville polyvalente, double réglage boucles + lacets.",
        "is_featured": False,
        "is_new_arrival": True,
    },
    {
        "src": "media_1795670013064_443b954f.webp",
        "dest": "estle-fw-08-widow-spider-creeper.webp",
        "name": "WIDOW SPIDER — EMBOSS CREEPER",
        "slug": "widow-spider-emboss-creeper",
        "sku": "EST-FW-008",
        "price": 98000,
        "compare_at": 110000,
        "short_description": "Creeper en cuir et daim noir avec toiles brodées et araignées métalliques 3D sur les œillets.",
        "description": "Finition atelier exceptionnelle : empiècements cuir lisse et suède noir, toiles d'araignées contrastées gris argent et 3 araignées sculptées en métal sur les pattes de laçage.",
        "fabric_specs": "Cuir lisse & suède noir, détails araignées métal argenté, semelle creeper 5 cm.",
        "cut_specs": "Coupe basse structurée, doublure intérieure cuir respirant.",
        "is_featured": False,
        "is_new_arrival": False,
    },
    {
        "src": "media_1795670013070_7d24dab2.webp",
        "dest": "estle-fw-09-memento-skull-hightop.webp",
        "name": "MEMENTO SKULL — TACTICAL HIGH-TOP",
        "slug": "memento-skull-tactical-high-top",
        "sku": "EST-FW-009",
        "price": 118000,
        "compare_at": 135000,
        "short_description": "Sneaker montante noire à harnais Cobra croisé, bijou de lacet crâne métal et bulle d'air.",
        "description": "Fusion gothic-techwear : tige haute en cuir grainé, mesh technique et texture carbone, verrouillée par sangles tactiques croisées, crâne en métal brossé et unité d'amorti Air.",
        "fabric_specs": "Cuir grainé, mesh balistique, empiècements carbone, boucles Cobra & crâne métal.",
        "cut_specs": "Coupe montante High-Top, amorti talon Air-Unit visible.",
        "is_featured": True,
        "is_new_arrival": True,
    },
    {
        "src": "media_1795670013064_f8476a9a.webp",
        "dest": "estle-fw-10-stealth-triple-buckle.webp",
        "name": "STEALTH MONOLITH — TRIPLE BUCKLE",
        "slug": "stealth-monolith-triple-buckle",
        "sku": "EST-FW-010",
        "price": 122000,
        "compare_at": None,
        "short_description": "Boot techwear furtive tout-noir à triple sangles tactiques et semelle géométrique carbone.",
        "description": "Design monochrome furtif conçu pour l'architecture urbaine : col néoprène & mesh technique, 3 boucles tactiques noires mates, renforts carbone et semelle géométrique ultra-légère.",
        "fabric_specs": "Nylon balistique, néoprène structuré, TPU mat, semelle composite carbone.",
        "cut_specs": "Tige mid-high ergonomique, triple serrage rapide sans contrainte.",
        "is_featured": True,
        "is_new_arrival": True,
    },
    {
        "src": "media_1795670031527_2ab973b4.webp",
        "dest": "estle-fw-11-indigo-denim-skate.webp",
        "name": "RAW INDIGO — DENIM COURT LOW",
        "slug": "raw-indigo-denim-court-low",
        "sku": "EST-FW-011",
        "price": 82000,
        "compare_at": 95000,
        "short_description": "Sneaker basse en denim indigo brut, suède marine, cuir crème et semelle gomme naturelle.",
        "description": "Pièce artisanale au contraste élégant : panneaux en denim selvedge délavé, cuir crème pleine fleur, surpiqûres sellier apparentes, lacets larges écru et semelle gomme rétro.",
        "fabric_specs": "Denim indigo lourd, suède marine, cuir crème, semelle caoutchouc gomme.",
        "cut_specs": "Coupe skate/court basse, languette matelassée épaisse.",
        "is_featured": True,
        "is_new_arrival": True,
    },
    {
        "src": "media_1795670031780_67eb8327.webp",
        "dest": "estle-fw-12-volt-pulse-runner.webp",
        "name": "VOLT PULSE — CHUNKY RUNNER",
        "slug": "volt-pulse-chunky-runner",
        "sku": "EST-FW-012",
        "price": 88000,
        "compare_at": None,
        "short_description": "Runner chunky gris anthracite et argent rehaussée d'accents jaune volt et rose néon.",
        "description": "Silhouette rétro-futuriste à semelle sculptée surdimensionnée, tige multicouche en nubuck gris et mesh respirant, dynamisée par des touches volt fluo et magenta.",
        "fabric_specs": "Nubuck gris anthracite, mesh respirant, semelle mousse double densité.",
        "cut_specs": "Coupe chunky running, amorti intégral ultra-confort.",
        "is_featured": False,
        "is_new_arrival": False,
    },
    {
        "src": "media_1795670031814_d1a200c7.webp",
        "dest": "estle-fw-13-chrome-carbon-runner.webp",
        "name": "CHROME CARBON — TECH RUNNER",
        "slug": "chrome-carbon-tech-runner",
        "sku": "EST-FW-013",
        "price": 96000,
        "compare_at": 110000,
        "short_description": "Runner métallique chrome et fibre de carbone avec système de laçage toggle et touches néon.",
        "description": "Édition cyber-métallique à finition argent miroir, inserts fibre de carbone dans la semelle intermédiaire, laçage rapide à bloqueur et détails volt & magenta.",
        "fabric_specs": "Cuir synthétique métallisé chrome, ripstop technique, inserts carbone.",
        "cut_specs": "Coupe technique légère, laçage rapide quick-toggle.",
        "is_featured": True,
        "is_new_arrival": True,
    },
    {
        "src": "media_1795670031814_2187a7c5.webp",
        "dest": "estle-fw-14-volt-apex-hightop.webp",
        "name": "VOLT APEX — HIGH-TOP RUNNER",
        "slug": "volt-apex-high-top-runner",
        "sku": "EST-FW-014",
        "price": 94000,
        "compare_at": None,
        "short_description": "Version montante de la runner architecturale gris anthracite, jaune volt et rose néon.",
        "description": "Tige haute matelassée à maintien cheville renforcé, œillets contrastés cramoisis, lacets mouchetés techniques et semelle sculptée bicolore à amorti supérieur.",
        "fabric_specs": "Cuir suédé gris, nylon matelassé, semelle EVA haute absorption.",
        "cut_specs": "Coupe montante High-Top, maintien cheville enveloppant.",
        "is_featured": False,
        "is_new_arrival": True,
    },
    {
        "src": "media_1795670031830_ef26aca4.webp",
        "dest": "estle-fw-15-crimson-deconstructed-high.webp",
        "name": "ARCHIVE 01 — DECONSTRUCTED CRIMSON",
        "slug": "archive-01-deconstructed-crimson",
        "sku": "EST-FW-015",
        "price": 128000,
        "compare_at": 145000,
        "short_description": "High-top déconstruite rouge cramoisi, blanc cassé et noir avec zip-tie signature et coutures apparentes.",
        "description": "Hommage au design déconstruit : empiècements cuir rouge et mesh translucide, Swoosh flottant maintenu par surpiqûres contrastées bleu/orange, zip-tie rouge et semelle marquée.",
        "fabric_specs": "Cuir pleine fleur rouge/blanc, mesh technique ripstop, semelle caoutchouc cousue.",
        "cut_specs": "Coupe High-Top iconique, languette mousse exposée.",
        "is_featured": True,
        "is_new_arrival": True,
    },
]

EU_SIZES = [
    ("EU 38", 6),
    ("EU 39", 8),
    ("EU 40", 12),
    ("EU 41", 14),
    ("EU 42", 16),
    ("EU 43", 14),
    ("EU 44", 10),
    ("EU 45", 6),
]

# 1. Copier les 15 images dans frontestle/public/images/footwear/
for item in SHOES:
    src_path = UPLOAD_DIR / item["src"]
    dest_path = PUBLIC_FOOTWEAR_DIR / item["dest"]
    if not src_path.exists():
        raise FileNotFoundError(f"Image introuvable: {src_path}")
    shutil.copy2(src_path, dest_path)

# 2. Récupérer (ou créer) la collection FOOTWEAR ARCHIVE
footwear_collection, _ = Collection.objects.get_or_create(
    slug="footwear-archive",
    defaults={
        "name": "FOOTWEAR ARCHIVE",
        "description": "Chaussures architecturales, bottes gothiques, creepers et runners techniques ESTLE.",
        "season": "DROP 2026",
        "is_active": True,
    },
)

# 3. Supprimer toutes les anciennes chaussures FOOTWEAR
old_qs = Product.objects.filter(category="FOOTWEAR")
deleted_count = old_qs.count()
old_qs.delete()
print(f"Anciennes chaussures supprimées : {deleted_count}")

# 4. Créer les 15 nouvelles chaussures avec 4 images dupliquées (FRONT, BACK, DETAIL, LOOKBOOK) + pointures EU 38-45
created_products = 0
for item in SHOES:
    img_url = f"/images/footwear/{item['dest']}"
    product = Product.objects.create(
        name=item["name"],
        slug=item["slug"],
        sku=item["sku"],
        collection=footwear_collection,
        category="FOOTWEAR",
        price_fcfa=item["price"],
        compare_at_price_fcfa=item["compare_at"],
        short_description=item["short_description"],
        description=item["description"],
        fabric_specs=item["fabric_specs"],
        cut_specs=item["cut_specs"],
        care_instructions="Nettoyage doux au chiffon microfibre humide. Conserver à l'abri de l'humidité directe dans le pochon ESTLE.",
        is_featured=item["is_featured"],
        is_new_arrival=item["is_new_arrival"],
        is_active=True,
    )

    gallery_views = [
        ("FRONT", "Vue Profil Principal — Showroom ESTLE", 0),
        ("BACK", "Vue Architecture & Semelle", 1),
        ("DETAIL", "Gros Plan Matières, Boucles & Finitions", 2),
        ("LOOKBOOK", "Présentation Éditoriale ESTLE Abidjan", 3),
    ]
    for view_type, caption, order in gallery_views:
        ProductImage.objects.create(
            product=product,
            image_url=img_url,
            view_type=view_type,
            caption=caption,
            display_order=order,
        )

    for size_label, stock_qty in EU_SIZES:
        size_code = size_label.replace(" ", "")
        ProductVariant.objects.create(
            product=product,
            size=size_label,
            color_name="Noir / Édition Archive",
            color_hex="#080808",
            stock=stock_qty,
            sku_variant=f"{item['sku']}-{size_code}",
        )

    created_products += 1

print(f"Nouvelles chaussures créées : {created_products}")
print(f"Images par chaussure : 4 (total {created_products * 4} ProductImage)")
print(f"Pointures EU par chaussure : {len(EU_SIZES)} (38 à 45)")
