"""
Loglama işlevleri.
"""
import os
import sys
from loguru import logger

from app.config import get_settings

settings = get_settings()

# Log dizininin varlığını kontrol et, yoksa oluştur
log_dir = os.path.dirname(settings.LOG_FILE)
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# Varsayılan logger'ı kaldır
logger.remove()

# Konsol logger'ı ekle
logger.add(
    sys.stderr,
    level=settings.LOG_LEVEL,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
)

# Dosya logger'ı ekle
logger.add(
    settings.LOG_FILE,
    level=settings.LOG_LEVEL,
    rotation="1 day",
    retention="7 days",
    compression="zip",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}"
)

def get_logger():
    """
    Yapılandırılmış logger'ı döndürür.
    """
    return logger