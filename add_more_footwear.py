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

NEW_SHOES = [
    {
        "src": "media_1795670414154_58145816.webp",
        "dest": "estle-fw-16-volt-titan-mega-platform.webp",
        "name": "VOLT TITAN — MEGA PLATFORM RUNNER",
        "slug": "volt-titan-mega-platform-runner",
        "sku": "EST-FW-016",
        "price": 112000,
        "compare_at": 128000,
        "short_description": "Runner double-plateforme sculptée gris anthracite, blanc pur et semelle crantée jaune volt.",
        "description": "Silhouette architecturale extrême à double semelle superposée, mêlant nubuck gris, mesh respirant, touches rose fluo et bloc cranté jaune volt haute élévation.",
        "fabric_specs": "Nubuck gris, mesh technique, double semelle EVA & caoutchouc cranté 8 cm.",
        "cut_specs": "Plateforme sculptée haute densité, amorti maximal.",
        "is_featured": True,
        "is_new_arrival": True,
    },
    {
        "src": "media_1795670414157_67568028.webp",
        "dest": "estle-fw-17-vanguard-tech-boot.webp",
        "name": "VANGUARD — TRIPLE STRAP TECH BOOT",
        "slug": "vanguard-triple-strap-tech-boot",
        "sku": "EST-FW-017",
        "price": 126000,
        "compare_at": None,
        "short_description": "Boot tactique furtive noir mat à 3 sangles à verrouillage rapide et talon blindé géométrique.",
        "description": "Conçue pour les environnements urbains exigeants : mesh balistique noir, contrefort talon géométrique moulé, triple sangles tactiques et semelle tout-terrain.",
        "fabric_specs": "Mesh balistique, TPU moulé mat, boucles tactiques noires, semelle trail.",
        "cut_specs": "Coupe mid-high tactique, maintien cheville sécurisé.",
        "is_featured": True,
        "is_new_arrival": True,
    },
    {
        "src": "media_1795670414177_3fdd51b4.webp",
        "dest": "estle-fw-18-apex-harness-combat.webp",
        "name": "APEX HARNESS — COMBAT TRAIL BOOT",
        "slug": "apex-harness-combat-trail-boot",
        "sku": "EST-FW-018",
        "price": 134000,
        "compare_at": 150000,
        "short_description": "Botte combat cuir et mesh noir à harnais Cobra, laçage toggle rapide et plaques métal.",
        "description": "Architecture lourde associant cuir grainé noir, mesh technique, sangles harnais à boucles Cobra, lacet élastique à bloqueur et renforts métalliques vissés sur la semelle.",
        "fabric_specs": "Cuir grainé noir, mesh balistique, boucles Cobra & plaques acier gunmetal.",
        "cut_specs": "Tige montante structurée, semelle crantée haute adhérence.",
        "is_featured": True,
        "is_new_arrival": True,
    },
    {
        "src": "media_1795670414179_fd9091b0.webp",
        "dest": "estle-fw-19-anarchy-studded-hightop.webp",
        "name": "ANARCHY — STUDDED CANVAS HIGH-TOP",
        "slug": "anarchy-studded-canvas-high-top",
        "sku": "EST-FW-019",
        "price": 96000,
        "compare_at": 110000,
        "short_description": "High-top en toile noire effilochée et cuir avec doubles boucles, clous pyramides, chaînes et épingles.",
        "description": "Esprit punk-gothique artisanal : toile canvas lourde noire, empiècements cuir, médaillon clouté, double sangles à boucles, chaînes latérales et épingles métalliques.",
        "fabric_specs": "Toile canvas 16 oz, cuir noir, clous pyramides & chaînes acier, semelle vulcanisée.",
        "cut_specs": "Coupe High-Top classique, bout renforcé caoutchouc clouté.",
        "is_featured": True,
        "is_new_arrival": True,
    },
    {
        "src": "media_1795670414182_bd6dd26c.webp",
        "dest": "estle-fw-20-crimson-victorian-heel.webp",
        "name": "VELVET CRIMSON — VICTORIAN LACE HEEL",
        "slug": "velvet-crimson-victorian-lace-heel",
        "sku": "EST-FW-020",
        "price": 120000,
        "compare_at": 138000,
        "short_description": "Bottine richelieu victorienne en cuir bordeaux, dentelle florale noire, ruban satin et talon sculpté.",
        "description": "Pièce couture néo-gothique : cuir bordeaux profond perforé façon brogue, incrustations de dentelle florale noire, œillets baroques, lacets ruban satin et talon aiguille ogival.",
        "fabric_specs": "Cuir bordeaux patiné, dentelle guipure noire, talon sculpté 9,5 cm.",
        "cut_specs": "Bout pointu élégant, laçage ruban satin réglable.",
        "is_featured": True,
        "is_new_arrival": True,
    },
    {
        "src": "media_1795670414175_e945fed1.webp",
        "dest": "estle-fw-21-reaper-skull-hightop.webp",
        "name": "REAPER — SKULL HARNESS HIGH-TOP",
        "slug": "reaper-skull-harness-high-top",
        "sku": "EST-FW-021",
        "price": 124000,
        "compare_at": None,
        "short_description": "Sneaker montante en cuir noir embossé baroque avec doubles brides gravées et breloques crânes métal.",
        "description": "Travail du cuir d'exception : gravures baroques ton-sur-ton au talon, suède noir, sangles croisées à boucles ciselées et charms crânes en métal vieilli.",
        "fabric_specs": "Cuir pleine fleur embossé, suède noir, boucles et crânes étain vieilli.",
        "cut_specs": "Coupe High-Top streetwear, semelle cupsole robuste.",
        "is_featured": True,
        "is_new_arrival": True,
    },
    {
        "src": "media_1795670414257_6a1a458f.webp",
        "dest": "estle-fw-22-spike-monolith-mid.webp",
        "name": "SPIKE MONOLITH — STUDDED MID BOOT",
        "slug": "spike-monolith-studded-mid-boot",
        "sku": "EST-FW-022",
        "price": 128000,
        "compare_at": 145000,
        "short_description": "Mid-boot cuir et suède noir à clous pyramides, pointes métalliques, chaîne et doubles boucles gravées.",
        "description": "Silhouette affirmée alliant cuir lisse, suède noir et languette embossée baroque, dotée de clous pyramides, chaîne latérale gunmetal et semelle tank crantée.",
        "fabric_specs": "Cuir noir & suède, clous & chaîne gunmetal, semelle tank crantée.",
        "cut_specs": "Hauteur mid-top cheville, double bride réglable.",
        "is_featured": False,
        "is_new_arrival": True,
    },
    {
        "src": "media_1795670456277_8687114c.webp",
        "dest": "estle-fw-23-alabaster-suede-court.webp",
        "name": "ALABASTER — MINIMAL SUEDE COURT",
        "slug": "alabaster-minimal-suede-court",
        "sku": "EST-FW-023",
        "price": 78000,
        "compare_at": None,
        "short_description": "Sneaker basse minimaliste en daim taupe et cuir perforé albâtre sur semelle crème épurée.",
        "description": "L'épure architecturale ESTLE au quotidien : panneaux en daim italien taupe doux, empeigne perforée blanc cassé et semelle cupsole ton-sur-ton ultra-confort.",
        "fabric_specs": "Daim velours taupe, cuir perforé albâtre, doublure cuir, semelle gomme crème.",
        "cut_specs": "Coupe basse court minimaliste, chaussant polyvalent.",
        "is_featured": True,
        "is_new_arrival": True,
    },
    {
        "src": "media_1795670456278_bfc425bb.webp",
        "dest": "estle-fw-24-pump-90-court-high.webp",
        "name": "PUMP 90 — RETRO COURT HIGH",
        "slug": "pump-90-retro-court-high",
        "sku": "EST-FW-024",
        "price": 108000,
        "compare_at": 125000,
        "short_description": "High-top basketball rétro blanc, noir et orange vif avec languette Pump et cage latérale TPU.",
        "description": "Icône des parquets années 90 : cuir pleine fleur blanc et noir contrasté, cage de maintien latérale TPU brillante, détails orange néon et système Pump sur la languette.",
        "fabric_specs": "Cuir pleine fleur, cage TPU, semelle EVA bi-densité.",
        "cut_specs": "Coupe montante basketball rétro, maintien cheville matelassé.",
        "is_featured": True,
        "is_new_arrival": False,
    },
    {
        "src": "media_1795670456501_375eb54c.webp",
        "dest": "estle-fw-25-navy-terrace-suede.webp",
        "name": "NAVY ARCHIVE — SUEDE TERRACE LOW",
        "slug": "navy-archive-suede-terrace-low",
        "sku": "EST-FW-025",
        "price": 75000,
        "compare_at": None,
        "short_description": "Sneaker terrace basse en daim bleu marine profond, bandes cuir crème et semelle rétro cassée.",
        "description": "Classique terrace intemporel revisité en daim marine velouté, bandes latérales crantées blanc cassé, talon cuir crème et semelle texturée vintage.",
        "fabric_specs": "Daim bleu marine, cuir lisse crème, semelle caoutchouc texturée.",
        "cut_specs": "Coupe basse fine et légère, confort quotidien.",
        "is_featured": False,
        "is_new_arrival": False,
    },
    {
        "src": "media_1795670456549_390a3604.webp",
        "dest": "estle-fw-26-sahara-air-tactical.webp",
        "name": "SAHARA AIR — TACTICAL STRAP MID",
        "slug": "sahara-air-tactical-strap-mid",
        "sku": "EST-FW-026",
        "price": 114000,
        "compare_at": 130000,
        "short_description": "Mid-top techwear sable et taupe à sangle centrale velcro, accents orange et bulle Air 270°.",
        "description": "Esthétique utilitaire désertique : mesh technique sable, empiècements daim beige, marquages techniques latéraux, bride velcro à pointe orange et unité Air 270° translucide.",
        "fabric_specs": "Mesh technique, daim sable, sangle velcro, unité Air 270° orange.",
        "cut_specs": "Coupe mid-top ergonomique, amorti talon extrême.",
        "is_featured": True,
        "is_new_arrival": True,
    },
    {
        "src": "media_1795670456549_1e1da1fd.webp",
        "dest": "estle-fw-27-reactor-gothic-platform.webp",
        "name": "REACTOR — GOTHIC CHUNKY PLATFORM",
        "slug": "reactor-gothic-chunky-platform",
        "sku": "EST-FW-027",
        "price": 138000,
        "compare_at": 158000,
        "short_description": "Boot-sneaker plateforme massive en cuir noir patiné, embossage toile d'araignée, zip et chaînes.",
        "description": "Pièce sculpturale lourde : cuir noir patiné effet usé, motif toile d'araignée embossé à l'avant, zip latéral, boucle centrale, chaînes métalliques et semelle réacteur massive.",
        "fabric_specs": "Cuir patiné noir, quincaillerie gunmetal, semelle plateforme sculptée 7 cm.",
        "cut_specs": "Forme Chunky Reactor, maintien cheville enveloppant.",
        "is_featured": True,
        "is_new_arrival": True,
    },
    {
        "src": "media_1795670456535_7262d4d2.webp",
        "dest": "estle-fw-28-pine-vault-high.webp",
        "name": "PINE VAULT — FOREST LEATHER HIGH",
        "slug": "pine-vault-forest-leather-high",
        "sku": "EST-FW-028",
        "price": 92000,
        "compare_at": 108000,
        "short_description": "High-top signature ESTLE en cuir grainé Vert Sapin Profond et noir mat avec bride cheville suède.",
        "description": "Aux couleurs emblématiques de la Maison ESTLE : cuir grainé Vert Sapin Profond (#0E2920), panneaux noir mat, bride velcro cheville en suède noir et semelle bicolore vert/noir.",
        "fabric_specs": "Cuir grainé vert sapin, cuir lisse noir, suède noir, semelle caoutchouc bicolore.",
        "cut_specs": "Coupe skate High-Top matelassée, bride de maintien supérieure.",
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

footwear_collection, _ = Collection.objects.get_or_create(
    slug="footwear-archive",
    defaults={
        "name": "FOOTWEAR ARCHIVE",
        "description": "Chaussures architecturales, bottes gothiques, creepers et runners techniques ESTLE.",
        "season": "DROP 2026",
        "is_active": True,
    },
)

created = 0
for item in NEW_SHOES:
    src_path = UPLOAD_DIR / item["src"]
    dest_path = PUBLIC_FOOTWEAR_DIR / item["dest"]
    if not src_path.exists():
        raise FileNotFoundError(f"Image introuvable: {src_path}")
    shutil.copy2(src_path, dest_path)

    # Éviter les doublons si le script est relancé
    Product.objects.filter(slug=item["slug"]).delete()

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
            color_name="Édition Archive",
            color_hex="#080808",
            stock=stock_qty,
            sku_variant=f"{item['sku']}-{size_code}",
        )

    created += 1

total_fw = Product.objects.filter(category="FOOTWEAR").count()
print(f"Nouvelles chaussures ajoutées : {created}")
print(f"Total Footwear en base : {total_fw}")
