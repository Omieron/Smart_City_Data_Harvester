"""
Uygulama ayarları ve konfigürasyon yönetimi.
"""
import os
from functools import lru_cache
from pydantic import BaseSettings, PostgresDsn

class Settings(BaseSettings):
    """Uygulama ayarları."""
    
    # Veritabanı
    DATABASE_URL: str
    
    # Scraper Ayarları
    SCRAPER_URL: str = "https://www.edremit.bel.tr/Guncel/NobetciE/"
    SCRAPE_HOUR: int = 15
    SCRAPE_MINUTE: int = 0
    
    # API Ayarları
    API_TITLE: str = "Edremit Nöbetçi Eczane API"
    API_VERSION: str = "1.0.0"
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    
    # Loglama
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/app.log"
    
    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    """Ayarları döndürür (önbellek ile)."""
    return Settings()