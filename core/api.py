from ninja import NinjaAPI
from accounts.api import router as accounts_router
from store.api import router as store_router

api = NinjaAPI(
    title="ESTLE — OFFICIAL WEBSITE ('The Art of Being Different.') API",
    version="1.0.0",
    description="API 100% Async/ASGI (Django Ninja + Pydantic v2) — Maison Gothic Streetwear Abidjan, Côte d'Ivoire.",
    docs_url="/docs",
)


@api.get("/health", tags=["Système"])
async def health_check(request):
    return {
        "status": "ok",
        "house": "ESTLE — The Art of Being Different.",
        "origin": "Abidjan, Côte d'Ivoire",
        "currency": "FCFA",
    }


api.add_router("/auth", accounts_router)
api.add_router("/", store_router)
