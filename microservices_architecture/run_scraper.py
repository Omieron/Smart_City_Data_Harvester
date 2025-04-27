"""
Bu script, eczane scraper'ını çalıştıran ana dosyadır.
Belirtilen saatte otomatik olarak çalıştırılacaktır.
"""
import os
import sys
import time
from dotenv import load_dotenv
from apscheduler.schedulers.background import BackgroundScheduler
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

from app.scraper.service import scrape_and_save
from app.scraper.scheduler import setup_scheduler

if __name__ == "__main__":
    logger.info("Eczane Scraper başlatılıyor...")
    
    # Günlük çalışma saati
    scrape_hour = int(os.getenv("SCRAPE_HOUR", 15))
    scrape_minute = int(os.getenv("SCRAPE_MINUTE", 0))
    
    # Scheduler'ı kur
    scheduler = setup_scheduler(scrape_hour, scrape_minute)
    scheduler.start()
    
    logger.info(f"Scheduler başlatıldı. Her gün saat {scrape_hour}:{scrape_minute:02d}'de çalışacak.")
    
    # Başlangıçta bir kez çalıştır
    logger.info("Başlangıç verisi çekiliyor...")
    scrape_and_save()
    
    try:
        # Uygulamayı çalışır durumda tut
        while True:
            time.sleep(60)
    except (KeyboardInterrupt, SystemExit):
        logger.info("Uygulama kapatılıyor...")
        scheduler.shutdown()