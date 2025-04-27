"""
Veritabanı bağlantı yönetimi.
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import get_settings
from loguru import logger
import psycopg2
from urllib.parse import urlparse

settings = get_settings()

# Database URL'ini log'la (hassas bilgileri maskeleyerek)
db_url = settings.DATABASE_URL
masked_db_url = db_url
if "://" in db_url:
    parts = db_url.split("://")
    if "@" in parts[1]:
        user_pass_host = parts[1].split("@")
        if ":" in user_pass_host[0]:
            user_pass = user_pass_host[0].split(":")
            masked_db_url = f"{parts[0]}://{user_pass[0]}:****@{user_pass_host[1]}"

logger.info(f"Veritabanına bağlanılıyor: {masked_db_url}")

# SQLAlchemy engine oluştur
try:
    engine = create_engine(settings.DATABASE_URL)
    logger.info("Veritabanı bağlantısı başarılı")
except Exception as e:
    logger.error(f"Veritabanı bağlantı hatası: {str(e)}")
    raise

# SessionLocal sınıfı oluştur
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Temel model sınıfı
Base = declarative_base()

def get_db():
    """Veritabanı oturumu oluştur ve kapat."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def check_database_connection():
    """
    Veritabanı bağlantısını test eder ve tablo bilgilerini gösterir.
    """
    try:
        # URL'den bağlantı bilgilerini ayıkla
        parsed = urlparse(settings.DATABASE_URL)
        db_user = parsed.username
        db_pass = parsed.password
        db_host = parsed.hostname
        db_port = parsed.port or 5432
        db_name = parsed.path[1:]  # Başındaki / karakterini kaldır
        
        logger.info(f"Veritabanı bilgileri:")
        logger.info(f"  Sunucu: {db_host}:{db_port}")
        logger.info(f"  Veritabanı: {db_name}")
        logger.info(f"  Kullanıcı: {db_user}")
        
        # Bağlantıyı test et
        conn = psycopg2.connect(
            host=db_host,
            port=db_port,
            dbname=db_name,
            user=db_user,
            password=db_pass
        )
        
        logger.info("Bağlantı başarılı!")
        
        # Tablo bilgilerini al
        with conn.cursor() as cur:
            # Tablo listesini al
            cur.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema='public'
            """)
            tables = cur.fetchall()
            
            if tables:
                logger.info("Veritabanındaki tablolar:")
                for table in tables:
                    table_name = table[0]
                    
                    # Tablo sütunlarını al
                    cur.execute("""
                        SELECT column_name, data_type 
                        FROM information_schema.columns 
                        WHERE table_name = %s
                    """, (table_name,))
                    
                    columns = cur.fetchall()
                    
                    # Tablo satır sayısını al
                    cur.execute(f"SELECT COUNT(*) FROM {table_name}")
                    row_count = cur.fetchone()[0]
                    
                    logger.info(f"  - {table_name} ({row_count} satır):")
                    for col in columns:
                        logger.info(f"      {col[0]} ({col[1]})")
            else:
                logger.warning("Veritabanında hiç tablo bulunamadı.")
        
        conn.close()
        return True
        
    except Exception as e:
        logger.error(f"Veritabanı bağlantı hatası: {str(e)}")
        return False