"""
FastAPI app ve ana router.
"""
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database.connection import engine, Base
from app.database import get_db
from app.api.routes import eczane_router

settings = get_settings()

# Veritabanı tablolarını oluştur
Base.metadata.create_all(bind=engine)

# FastAPI uygulamasını oluştur
app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    description="Edremit Nöbetçi Eczane bilgilerini sunan API"
)

# CORS ayarları
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Alt routerları ekle
app.include_router(eczane_router, prefix="/api", tags=["eczaneler"])

@app.get("/", tags=["root"])
def ana_sayfa():
    """Ana sayfa."""
    return {
        "mesaj": "Edremit Nöbetçi Eczane API'sine hoş geldiniz.",
        "versiyon": settings.API_VERSION,
        "dokumantasyon": "/docs"
    }

@app.get("/health", tags=["health"])
def health_check(db: Session = Depends(get_db)):
    """Sağlık kontrolü."""
    # Veritabanı bağlantısını kontrol et
    try:
        db.execute("SELECT 1")
        db_status = "bağlantı başarılı"
    except Exception as e:
        db_status = f"bağlantı hatası: {str(e)}"
    
    return {
        "status": "çalışıyor",
        "database": db_status
    }