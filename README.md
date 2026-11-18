# 🏛 ESTLE — OFFICIAL BACKEND API
> *"The Art of Being Different."*

Backend asynchrone haute performance propulsé par **Django Ninja** et architecture ASGI pour la plateforme e-commerce et boutique virtuelle 3D **ESTLE** (Abidjan, Côte d'Ivoire).

---

## 🛠 Stack Technique
- **Framework :** [Python 3.12+](https://www.python.org/) & [Django 5.1+](https://www.djangoproject.com/)
- **API Engine :** [Django Ninja](https://django-ninja.dev/) (Architecture 100% Asynchrone ASGI sous Uvicorn)
- **Validation :** [Pydantic v2](https://docs.pydantic.dev/latest/)
- **Base de Données :** PostgreSQL (production) & SQLite async (développement)
- **Authentification :** JWT sécurisé (`django-ninja-jwt`) pour clients & administration
- **Sécurité :** Rate-limiting, CORS sécurisé, hachage PBKDF2/Argon2, schémas stricts

---

## 📁 Architecture des Modules

```
backestle/
├── accounts/          # Authentification JWT, profil utilisateur, rôles Admin/Client
│   ├── api.py         # Endpoints async register, login, refresh, profile
│   └── models.py      # CustomUser (email unique, devise FCFA, téléphone)
├── store/             # Catalogue produits, collections, CMS, commandes & paiements
│   ├── api.py         # Endpoints async CRUD produits, stocks, collections, checkout
│   ├── models.py      # Product, ProductImage, Collection, Order, OrderItem, PaymentMethodConfig, SiteContent
│   └── schemas.py     # Schémas Pydantic v2 stricts
├── core/              # Configuration globale ASGI, settings, CORS, URLs
│   ├── api.py         # Routeur central NinjaAPI (v1)
│   ├── asgi.py        # Point d'entrée asynchrone ASGI
│   └── settings.py    # Configuration Django sécurisée
├── docker-compose.yml # PostgreSQL 16 ready
├── requirements.txt   # Dépendances Python
└── seed_data.py       # Script d'initialisation des collections, produits et CMS
```

---

## 🚀 Démarrage Rapide

### 1. Création de l'environnement virtuel & installation
```bash
python -m venv venv
.\venv\Scripts\activate   # Windows
# source venv/bin/activate # Linux/macOS
pip install -r requirements.txt
```

### 2. Configuration `.env`
Copiez le fichier `.env.example` en `.env` :
```env
DEBUG=True
SECRET_KEY=estle_secret_key_development_only
ALLOWED_HOSTS=127.0.0.1,localhost
DB_ENGINE=django.db.backends.sqlite3
DB_NAME=db.sqlite3
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

### 3. Migrations & Données de démonstration
```bash
python manage.py migrate
python seed_data.py
```

### 4. Lancement du serveur ASGI
```bash
python manage.py runserver
# Ou directement avec Uvicorn :
# uvicorn core.asgi:application --reload --port 8000
```
La documentation interactive OpenAPI / Swagger est accessible sur :
[http://127.0.0.1:8000/api/v1/docs](http://127.0.0.1:8000/api/v1/docs).
