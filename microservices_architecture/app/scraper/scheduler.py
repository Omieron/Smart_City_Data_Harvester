"""
Zamanlama işlemleri.
"""
from apscheduler.schedulers.background import BackgroundScheduler
from loguru import logger

from app.scraper.service import scrape_and_save

def setup_scheduler(hour: int, minute: int) -> BackgroundScheduler:
    """
    Belirtilen saat ve dakikada çalışacak bir scheduler oluşturur.
    
    Args:
        hour: Çalışma saati (24 saat formatında)
        minute: Çalışma dakikası
        
    Returns:
        BackgroundScheduler: Ayarlanmış scheduler nesnesi
    """
    scheduler = BackgroundScheduler()
    
    # Her gün belirtilen saatte çalışacak job ekle
    scheduler.add_job(
        scrape_and_save,
        'cron',
        hour=hour,
        minute=minute,
        id='daily_scrape',
        replace_existing=True,
        misfire_grace_time=60  # 1 dakikalık gecikme toleransı
    )
    
    logger.info(f"Scheduler ayarlandı. Her gün saat {hour}:{minute:02d}'de çalışacak.")
    
    return scheduler