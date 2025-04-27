"""
Bu script, FastAPI uygulamasını çalıştıran ana dosyadır.
"""
import os
import sys
import uvicorn
from dotenv import load_dotenv
from loguru import logger

# Projenin kök dizinini sys.path'e ekle
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# .env dosyasını yükle
load_dotenv()

# Logging ayarları
logger.add(
    os.getenv("LOG_FILE", "logs/app.log"),
    level=os.getenv("LOG_LEVEL", "INFO"),
    rotation="1 day",
    retention="7 days",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"
)

if __name__ == "__main__":
    logger.info("Eczane API başlatılıyor...")
    
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", 8000))
    
    uvicorn.run(
        "app.api.main:app",
        host=host,
        port=port,
        reload=True
    )