from django.core.management.base import BaseCommand
from accounts.models import CustomUser
from store.models import (
    Collection,
    PaymentMethodConfig,
    Product,
    ProductImage,
    ProductVariant,
    SiteContent,
)


class Command(BaseCommand):
    help = "Initialise la base de données officielle ESTLE — Gothic Streetwear Abidjan (Côte d'Ivoire)"

    def handle(self, *args, **options):
        self.stdout.write("Initialisation de la Maison ESTLE — Abidjan...")

        # 1. Comptes Administrateurs
        for email, pwd in [
            ("admin@estle.ci", "EstleAbidjan2026!"),
            ("admin@estle.com", "AdminPassword123!"),
        ]:
            if not CustomUser.objects.filter(email=email).exists():
                CustomUser.objects.create_superuser(
                    email=email,
                    password=pwd,
                    first_name="Direction",
                    last_name="ESTLE Abidjan",
                    phone_number="+225 07 00 00 00 00",
                    default_city="Abidjan",
                    default_commune="Cocody Riviera",
                    default_address="Boulevard de France, Atelier ESTLE",
                )
                self.stdout.write(self.style.SUCCESS(f"✓ Superuser créé : {email} / {pwd}"))

        # 2. Contenus CMS du site (SiteContent)
        cms_entries = [
            {
                "key": "hero_main",
                "title": "ESTLE — THE ART OF BEING DIFFERENT.",
                "subtitle": "MAISON INDÉPENDANTE DE GOTHIC STREETWEAR • ABIDJAN, CÔTE D'IVOIRE",
                "body": (
                    "Née dans l'effervescence nocturne d'Abidjan, ESTLE façonne une garde-robe architecturale "
                    "où l'obscurité rencontre la rigueur du tailoring contemporain. Chaque pièce est pensée "
                    "comme un monolithe textile en coton lourd et teintures minérales."
                ),
                "cta_label": "ENTRER DANS LA GALERIE 360°",
            },
            {
                "key": "manifesto",
                "title": "WE ARE NOT HERE TO FIT IN.",
                "subtitle": "MANIFESTE ARCHITECTURAL — ABIDJAN / MONDE",
                "body": (
                    "Nous refusons l'uniformité bruyante. Notre esthétique puise dans le silence des volumes "
                    "brutalistes, les drapés asymétriques et la noblesse des matières denses (500+ GSM). "
                    "De Cocody à Tokyo, ESTLE incarne l'art d'être résolument différent."
                ),
                "cta_label": "DÉCOUVRIR LES ARCHIVES",
            },
            {
                "key": "shipping_ci",
                "title": "EXPÉDITION PRIVÉE CÔTE D'IVOIRE & INTERNATIONAL",
                "subtitle": "Coursier dédié Abidjan (24h) & Expédition Nationale (48h)",
                "body": (
                    "Livraison par coursier privé sur toutes les communes d'Abidjan (Cocody, Plateau, Marcory, "
                    "Zone 4, Riviera, Yopougon) et expédition sécurisée vers Yamoussoukro, Bouaké, San-Pédro et Korhogo."
                ),
                "cta_label": "VOIR LES CONDITIONS",
            },
        ]
        for entry in cms_entries:
            SiteContent.objects.update_or_create(key=entry["key"], defaults=entry)

        # 3. Moyens de paiement Côte d'Ivoire (PaymentMethodConfig)
        payment_configs = [
            {
                "code": "WAVE",
                "name": "Wave Côte d'Ivoire",
                "description": "Paiement mobile instantané via l'application Wave CI (+225).",
                "instructions": "Confirmation immédiate sans frais supplémentaires à la validation.",
                "badge_label": "Actif • Instantané 0% frais",
                "is_active": True,
                "display_order": 1,
            },
            {
                "code": "ORANGE_MONEY",
                "name": "Orange Money Côte d'Ivoire",
                "description": "Règlement sécurisé par Orange Money CI (#144# ou application Max it).",
                "instructions": "Code marchand ESTLE Abidjan validé instantanément.",
                "badge_label": "Actif • Sécurisé #144#",
                "is_active": True,
                "display_order": 2,
            },
            {
                "code": "MTN_MOMO",
                "name": "MTN Mobile Money (MoMo)",
                "description": "Passerelle MTN MoMo Côte d'Ivoire en cours d'intégration finale.",
                "instructions": "Passerelle bientôt disponible.",
                "badge_label": "Bientôt disponible",
                "is_active": False,
                "display_order": 3,
            },
            {
                "code": "CARD",
                "name": "Carte Bancaire (Visa / Mastercard)",
                "description": "Paiement international 3D-Secure par carte bancaire.",
                "instructions": "Module bancaire international bientôt disponible.",
                "badge_label": "Bientôt disponible",
                "is_active": False,
                "display_order": 4,
            },
        ]
        for pm in payment_configs:
            PaymentMethodConfig.objects.update_or_create(code=pm["code"], defaults=pm)

        # 4. Les 4 Vitrines / Collections ESTLE
        collections_data = [
            {
                "code": "01 — STREETWEAR",
                "name": "OBSIDIAN DRAPERY",
                "slug": "obsidian-drapery",
                "subtitle": "Draperie Technique & Jersey Lourd 540 GSM",
                "description": (
                    "Silhouettes surdimensionnées en coton peigné haute densité, coutures retournées "
                    "et traitements tinctoriaux noir obsidienne et vert sapin profond."
                ),
                "editorial_quote": "« La matière absorbe la lumière pour ne laisser parler que la coupe. »",
                "hero_image": "https://images.unsplash.com/photo-1509631179647-0177331693ae?w=1400&auto=format&fit=crop&q=85",
                "secondary_image": "https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?w=1200&auto=format&fit=crop&q=80",
                "accent_color": "#0E2920",
                "showcase_index": 1,
                "shader_type": "cloth",
                "is_featured": True,
            },
            {
                "code": "02 — MEN",
                "name": "MONOLITH TAILORING",
                "slug": "monolith-tailoring",
                "subtitle": "Architecture Masculine & Lignes Brutalistes",
                "description": (
                    "Vestes structurées, pantalons cargo sculpturaux à sangles dissimulées et pardessus "
                    "sans col inspirés de l'architecture contemporaine d'Abidjan."
                ),
                "editorial_quote": "« Une armure silencieuse taillée pour traverser la nuit urbaine. »",
                "hero_image": "https://images.unsplash.com/photo-1617137984095-74e4e5e3613f?w=1400&auto=format&fit=crop&q=85",
                "secondary_image": "https://images.unsplash.com/photo-1507679799987-c73779587ccf?w=1200&auto=format&fit=crop&q=80",
                "accent_color": "#9A8253",
                "showcase_index": 2,
                "shader_type": "monolith",
                "is_featured": True,
            },
            {
                "code": "03 — COLLECTIONS",
                "name": "NOCTURNE PINE ARCHIVE",
                "slug": "nocturne-pine-archive",
                "subtitle": "Édition Limitée Numérotée — Vert Sapin & Or Sombre",
                "description": (
                    "L'alliance signature d'ESTLE : des pièces d'archive mêlant broderies métalliques "
                    "or sombre (#9A8253) sur velours technique et gabardine vert sapin (#0E2920)."
                ),
                "editorial_quote": "« Chaque pièce porte un numéro d'archive unique gravé à l'atelier. »",
                "hero_image": "https://images.unsplash.com/photo-1539109136881-3be0616acf4b?w=1400&auto=format&fit=crop&q=85",
                "secondary_image": "https://images.unsplash.com/photo-1487222477894-8943e31ef7b2?w=1200&auto=format&fit=crop&q=80",
                "accent_color": "#1B4D3E",
                "showcase_index": 3,
                "shader_type": "liquid",
                "is_featured": True,
            },
            {
                "code": "04 — NEW ARRIVALS",
                "name": "KINETIC SHADOW DROP 04",
                "slug": "kinetic-shadow-drop-04",
                "subtitle": "Nouvelles Silhouettes Avant-Garde 2026",
                "description": (
                    "Les dernières créations sorties de notre laboratoire textile : coupes asymétriques, "
                    "superpositions modulaires et traitements déperlants mats."
                ),
                "editorial_quote": "« Le futur du streetwear africain s'écrit dans la maîtrise du volume. »",
                "hero_image": "https://images.unsplash.com/photo-1552374196-1ab2a1c593e8?w=1400&auto=format&fit=crop&q=85",
                "secondary_image": "https://images.unsplash.com/photo-1490481651871-ab68de25d43d?w=1200&auto=format&fit=crop&q=80",
                "accent_color": "#9A8253",
                "showcase_index": 4,
                "shader_type": "kinetic",
                "is_featured": True,
            },
        ]

        cols = {}
        for c_data in collections_data:
            col, _ = Collection.objects.update_or_create(slug=c_data["slug"], defaults=c_data)
            cols[c_data["slug"]] = col

        # 5. Les 8 Pièces Gothic Streetwear ESTLE (Prix en FCFA)
        products_data = [
            {
                "collection": cols["obsidian-drapery"],
                "category": "STREETWEAR",
                "name": "HOODIE ARCHITECTURAL 'VOID 540'",
                "slug": "hoodie-architectural-void-540",
                "sku": "ESTLE-SW-001",
                "price_fcfa": 85000,
                "compare_at_price_fcfa": 95000,
                "short_description": "Molleton lourd 540 GSM à capuche sculpturale doublée et épaules tombantes.",
                "description": (
                    "Conçu dans notre atelier d'Abidjan à partir d'un jersey de coton peigné 540 GSM, "
                    "le Hoodie VOID 540 présente une coupe boxy architecturale sans cordons apparents. "
                    "Ses coutures inversées sur les omoplates et sa poche kangourou dissimulée dans la découpe "
                    "latérale offrent un tombé franc et sculptural."
                ),
                "fabric_specs": "100% Coton Peigné Lourd 540 GSM • Teinture minérale Obsidian Black",
                "cut_specs": "Coupe Boxy Oversize • Épaules tombantes +6cm • Capuche double épaisseur",
                "care_instructions": "Lavage main ou machine 30°C cycle délicat à l'envers • Séchage à plat",
                "shader_preset": "cloth",
                "is_new_arrival": True,
                "is_featured": True,
                "images": [
                    (
                        "FRONT",
                        "https://images.unsplash.com/photo-1556821840-3a63f95609a7?w=1200&auto=format&fit=crop&q=85",
                        "Vue de Face — Volume boxy 540 GSM",
                    ),
                    (
                        "BACK",
                        "https://images.unsplash.com/photo-1578681994506-b8f463449011?w=1200&auto=format&fit=crop&q=85",
                        "Vue de Dos — Coutures dorsales inversées",
                    ),
                    (
                        "DETAIL",
                        "https://images.unsplash.com/photo-1620799140408-edc6dcb6d633?w=1200&auto=format&fit=crop&q=85",
                        "Macro — Grain du coton 540 GSM & broderie ton sur ton",
                    ),
                ],
                "colors": [("Obsidian Black", "#080808"), ("Deep Pine", "#0E2920")],
            },
            {
                "collection": cols["obsidian-drapery"],
                "category": "STREETWEAR",
                "name": "T-SHIRT DRAPÉ ASYMÉTRIQUE 'Kuro-CI'",
                "slug": "t-shirt-drape-asymetrique-kuro-ci",
                "sku": "ESTLE-SW-002",
                "price_fcfa": 45000,
                "compare_at_price_fcfa": None,
                "short_description": "Jersey 320 GSM à ourlet asymétrique et col montant côtelé épais.",
                "description": (
                    "Une réinterprétation radicale du t-shirt essentiel. Doté d'un col ras-du-cou de 3,5 cm "
                    "indéformable, de manches allongées jusqu'au coude et d'un pan d'ourlet diagonal qui "
                    "accompagne le mouvement du corps avec fluidité."
                ),
                "fabric_specs": "100% Coton Organique 320 GSM • Toucher carbone brossé",
                "cut_specs": "Coupe Longline Asymétrique • Manches mi-longues",
                "care_instructions": "Lavage à froid 30°C • Repassage vapeur doux sur l'envers",
                "shader_preset": "cloth",
                "is_new_arrival": False,
                "is_featured": True,
                "images": [
                    (
                        "FRONT",
                        "https://images.unsplash.com/photo-1521572267360-ee0c2909d518?w=1200&auto=format&fit=crop&q=85",
                        "Vue de Face — Drapé diagonal",
                    ),
                    (
                        "BACK",
                        "https://images.unsplash.com/photo-1583743814966-8936f5b7be1a?w=1200&auto=format&fit=crop&q=85",
                        "Vue de Dos — Ligne verticale signature ESTLE",
                    ),
                    (
                        "DETAIL",
                        "https://images.unsplash.com/photo-1503342217505-b0a15ec3261c?w=1200&auto=format&fit=crop&q=85",
                        "Macro — Col côtelé haute densité 35mm",
                    ),
                ],
                "colors": [("Obsidian Black", "#080808"), ("Raw Anthracite", "#1C1C1C")],
            },
            {
                "collection": cols["monolith-tailoring"],
                "category": "MEN",
                "name": "PANTALON CARGO MONOLITHE 'ABIDJAN ZERO'",
                "slug": "pantalon-cargo-monolithe-abidjan-zero",
                "sku": "ESTLE-MEN-001",
                "price_fcfa": 110000,
                "compare_at_price_fcfa": 125000,
                "short_description": "Gabardine de coton technique à 6 poches soufflets biseautées et sangles internes.",
                "description": (
                    "Pièce maîtresse du vestiaire masculin ESTLE. Ce pantalon cargo en gabardine dense combine "
                    "une jambe large structurée avec des pattes de serrage aux chevilles permettant de basculer "
                    "d'un tombé droit architectural à un volume resserré sur la chaussure."
                ),
                "fabric_specs": "Gabardine Technique 410 GSM • Déperlant mat • Bouclerie métal noir mat",
                "cut_specs": "Coupe Wide-Leg Structurée • Chevilles ajustables par boutons-pression",
                "care_instructions": "Nettoyage délicat 30°C • Ne pas sécher en tambour",
                "shader_preset": "monolith",
                "is_new_arrival": True,
                "is_featured": True,
                "images": [
                    (
                        "FRONT",
                        "https://images.unsplash.com/photo-1624378439575-d8705ad7ae80?w=1200&auto=format&fit=crop&q=85",
                        "Vue de Face — Poches soufflets architecturales",
                    ),
                    (
                        "BACK",
                        "https://images.unsplash.com/photo-1517445312882-bc9910d016b7?w=1200&auto=format&fit=crop&q=85",
                        "Vue de Dos — Découpes articulées aux genoux",
                    ),
                    (
                        "DETAIL",
                        "https://images.unsplash.com/photo-1541099649105-f69ad21f3246?w=1200&auto=format&fit=crop&q=85",
                        "Macro — Sangle de réglage et rivet gravé ESTLE",
                    ),
                ],
                "colors": [("Obsidian Black", "#080808"), ("Deep Pine", "#0E2920")],
            },
            {
                "collection": cols["monolith-tailoring"],
                "category": "MEN",
                "name": "MANTEAU SANS COL 'SILENCE BRUT'",
                "slug": "manteau-sans-col-silence-brut",
                "sku": "ESTLE-MEN-002",
                "price_fcfa": 165000,
                "compare_at_price_fcfa": 190000,
                "short_description": "Pardessus mi-long à encolure franche, boutonnage caché et doublure satin or sombre.",
                "description": (
                    "Inspiré des vestes monastiques et du tailoring japonais, le manteau SILENCE BRUT épure "
                    "toute ornementation superflue. Son ouverture frontale nette révèle à chaque mouvement "
                    "un passepoil intérieur en or sombre (#9A8253)."
                ),
                "fabric_specs": "Laine Froide & Coton Technique • Doublure viscose respirante",
                "cut_specs": "Coupe Droite Architecturale • Épaules carrées naturelles",
                "care_instructions": "Nettoyage à sec uniquement",
                "shader_preset": "monolith",
                "is_new_arrival": False,
                "is_featured": True,
                "images": [
                    (
                        "FRONT",
                        "https://images.unsplash.com/photo-1539533018447-63fcce2678e3?w=1200&auto=format&fit=crop&q=85",
                        "Vue de Face — Ligne monolithique sans revers",
                    ),
                    (
                        "BACK",
                        "https://images.unsplash.com/photo-1507679799987-c73779587ccf?w=1200&auto=format&fit=crop&q=85",
                        "Vue de Dos — Fente médiane haute",
                    ),
                    (
                        "DETAIL",
                        "https://images.unsplash.com/photo-1490481651871-ab68de25d43d?w=1200&auto=format&fit=crop&q=85",
                        "Macro — Passepoil intérieur Or Sombre #9A8253",
                    ),
                ],
                "colors": [("Obsidian Black", "#080808"), ("Raw Anthracite", "#1C1C1C")],
            },
            {
                "collection": cols["nocturne-pine-archive"],
                "category": "COLLECTIONS",
                "name": "VESTE KIMONO ARCHIVE 'PINE & GOLD N°03'",
                "slug": "veste-kimono-archive-pine-gold-03",
                "sku": "ESTLE-COL-001",
                "price_fcfa": 145000,
                "compare_at_price_fcfa": None,
                "short_description": "Veste croisée vert sapin profond à surpiqûres fil d'or vieilli et ceinture intégrée.",
                "description": (
                    "Édition numérotée issue de la Collection 03. Taillée dans un sergé vert sapin profond "
                    "(#0E2920) aux reflets nocturnes, cette veste croisée s'ajuste par un système de liens "
                    "internes et arbore l'emblème géométrique ESTLE brodé au fil d'or sombre."
                ),
                "fabric_specs": "Sergé Japonais 440 GSM • Broderie fil métallique Aged Gold",
                "cut_specs": "Coupe Croisée Kimono • Manches amples structurées",
                "care_instructions": "Nettoyage à sec recommandé",
                "shader_preset": "liquid",
                "is_new_arrival": True,
                "is_featured": True,
                "images": [
                    (
                        "FRONT",
                        "https://images.unsplash.com/photo-1539109136881-3be0616acf4b?w=1200&auto=format&fit=crop&q=85",
                        "Vue de Face — Croisement asymétrique Vert Sapin",
                    ),
                    (
                        "BACK",
                        "https://images.unsplash.com/photo-1509631179647-0177331693ae?w=1200&auto=format&fit=crop&q=85",
                        "Vue de Dos — Broderie géométrique Or Sombre",
                    ),
                    (
                        "DETAIL",
                        "https://images.unsplash.com/photo-1487222477894-8943e31ef7b2?w=1200&auto=format&fit=crop&q=85",
                        "Macro — Numérotation d'archive cousue main",
                    ),
                ],
                "colors": [("Deep Pine", "#0E2920"), ("Obsidian Black", "#080808")],
            },
            {
                "collection": cols["nocturne-pine-archive"],
                "category": "COLLECTIONS",
                "name": "CHEMISE OVERSHIRT 'CHIAROSCURO'",
                "slug": "chemise-overshirt-chiaroscuro",
                "sku": "ESTLE-COL-002",
                "price_fcfa": 78000,
                "compare_at_price_fcfa": 88000,
                "short_description": "Surchemise lourde à poches poitrine dissimulées et boutons en corne fumée.",
                "description": (
                    "Conçue pour être portée aussi bien ouverte sur un t-shirt drapé que fermée comme une "
                    "veste légère. Son tissage texturé capte la lumière rasante avec élégance."
                ),
                "fabric_specs": "Coton Texturé 380 GSM • Boutons corne naturelle noire",
                "cut_specs": "Coupe Relaxed Boxy • Ourlet droit fendu",
                "care_instructions": "Lavage 30°C • Séchage sur cintre large",
                "shader_preset": "liquid",
                "is_new_arrival": False,
                "is_featured": True,
                "images": [
                    (
                        "FRONT",
                        "https://images.unsplash.com/photo-1617137984095-74e4e5e3613f?w=1200&auto=format&fit=crop&q=85",
                        "Vue de Face — Tombé structuré",
                    ),
                    (
                        "BACK",
                        "https://images.unsplash.com/photo-1552374196-1ab2a1c593e8?w=1200&auto=format&fit=crop&q=85",
                        "Vue de Dos — Empiècement d'épaule doublé",
                    ),
                    (
                        "DETAIL",
                        "https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?w=1200&auto=format&fit=crop&q=85",
                        "Macro — Bouton en corne fumée gravé",
                    ),
                ],
                "colors": [("Deep Pine", "#0E2920"), ("Aged Gold", "#9A8253")],
            },
            {
                "collection": cols["kinetic-shadow-drop-04"],
                "category": "NEW_ARRIVALS",
                "name": "BOMBER SCULPTURAL 'ECLIPSE MA-1'",
                "slug": "bomber-sculptural-eclipse-ma1",
                "sku": "ESTLE-NEW-001",
                "price_fcfa": 135000,
                "compare_at_price_fcfa": None,
                "short_description": "Bomber volume cocon en nylon mat haute densité avec zip double-curseur doré.",
                "description": (
                    "Nouveauté Drop 04 : Le bomber ECLIPSE réinvente les proportions classiques avec des "
                    "manches froncées haute couture, un dos bombé et une fermeture éclair métallique "
                    "en finition or vieilli (#9A8253)."
                ),
                "fabric_specs": "Nylon Tactique Mat 100% Déperlant • Doublure matelassée légère",
                "cut_specs": "Coupe Cropped Volumineuse • Poignets bord-côte lourd",
                "care_instructions": "Nettoyage à sec ou éponge humide",
                "shader_preset": "kinetic",
                "is_new_arrival": True,
                "is_featured": True,
                "images": [
                    (
                        "FRONT",
                        "https://images.unsplash.com/photo-1551028719-00167b16eac5?w=1200&auto=format&fit=crop&q=85",
                        "Vue de Face — Volume cocon & zip Or Sombre",
                    ),
                    (
                        "BACK",
                        "https://images.unsplash.com/photo-1544441893-675973e31985?w=1200&auto=format&fit=crop&q=85",
                        "Vue de Dos — Pli d'aisance dorsal architectural",
                    ),
                    (
                        "DETAIL",
                        "https://images.unsplash.com/photo-1591047139829-d91aecb6caea?w=1200&auto=format&fit=crop&q=85",
                        "Macro — Zip métallique Aged Gold & fronces manches",
                    ),
                ],
                "colors": [("Obsidian Black", "#080808"), ("Deep Pine", "#0E2920")],
            },
            {
                "collection": cols["kinetic-shadow-drop-04"],
                "category": "NEW_ARRIVALS",
                "name": "SAC CROSSBODY ARCHITECTURAL 'OBELISK'",
                "slug": "sac-crossbody-architectural-obelisk",
                "sku": "ESTLE-NEW-002",
                "price_fcfa": 65000,
                "compare_at_price_fcfa": 75000,
                "short_description": "Cuir grainé noir mat et toile balistique à boucle magnétique rapide.",
                "description": (
                    "Conçu pour accompagner les silhouettes ESTLE, le sac OBELISK épouse le buste grâce "
                    "à sa géométrie trapézoïdale rigide et sa sangle industrielle réglable."
                ),
                "fabric_specs": "Cuir Pleine Fleur Grainé & Nylon Balistique 1680D",
                "cut_specs": "Format Trapèze Rigide • Bandoulière réglable 120cm",
                "care_instructions": "Entretien lait cuir neutre",
                "shader_preset": "kinetic",
                "is_new_arrival": True,
                "is_featured": True,
                "images": [
                    (
                        "FRONT",
                        "https://images.unsplash.com/photo-1548036328-c9fa89d128fa?w=1200&auto=format&fit=crop&q=85",
                        "Vue de Face — Géométrie trapézoïdale",
                    ),
                    (
                        "BACK",
                        "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=1200&auto=format&fit=crop&q=85",
                        "Vue de Dos — Sangle tactique articulée",
                    ),
                    (
                        "DETAIL",
                        "https://images.unsplash.com/photo-1590874103328-eac38a683ce7?w=1200&auto=format&fit=crop&q=85",
                        "Macro — Plaque métallique gravée ESTLE Abidjan",
                    ),
                ],
                "colors": [("Obsidian Black", "#080808"), ("Aged Gold", "#9A8253")],
            },
        ]

        # Nettoyage des anciens produits de démo génériques s'ils existent
        Product.objects.exclude(slug__in=[p["slug"] for p in products_data]).delete()

        for p_item in products_data:
            imgs = p_item.pop("images")
            colors = p_item.pop("colors")
            product, _ = Product.objects.update_or_create(slug=p_item["slug"], defaults=p_item)

            ProductImage.objects.filter(product=product).delete()
            for idx, (vtype, url, cap) in enumerate(imgs):
                ProductImage.objects.create(
                    product=product,
                    view_type=vtype,
                    image_url=url,
                    caption=cap,
                    display_order=idx,
                )

            ProductVariant.objects.filter(product=product).delete()
            for sz in ["S", "M", "L", "XL"]:
                for c_name, c_hex in colors:
                    sku_var = f"{product.sku}-{sz}-{c_name[:3].upper()}"
                    ProductVariant.objects.create(
                        product=product,
                        size=sz,
                        color_name=c_name,
                        color_hex=c_hex,
                        stock=12,
                        sku_variant=sku_var,
                    )

            self.stdout.write(f"  ✓ Pièce initialisée : {product.name} ({product.price_fcfa} FCFA)")

        self.stdout.write(self.style.SUCCESS("✨ Maison ESTLE — Initialisation terminée avec succès !"))
