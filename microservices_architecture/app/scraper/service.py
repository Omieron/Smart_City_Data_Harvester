"""
Scraper ana işlevsellik.
"""
import datetime
import traceback
from typing import List
from sqlalchemy.orm import Session
from loguru import logger

from app.config import get_settings
from app.database.connection import SessionLocal
from app.database.models import Eczane as EczaneModel, NobetciEczane as NobetciEczaneModel
from app.database.schemas import ScraperEczane
from app.scraper.parser import parse_eczane_data

settings = get_settings()

def scrape_and_save():
    """
    Web sitesinden nöbetçi eczane bilgilerini çeker ve veritabanına kaydeder.
    """
    try:
        logger.info("Veri çekme işlemi başlatılıyor...")
        
        # Web sitesinden veri çek
        eczane_verileri = parse_eczane_data(settings.SCRAPER_URL)
        
        # Veri yoksa işlemi durdur
        if not eczane_verileri:
            logger.warning("Çekilecek veri bulunamadı.")
            return
        
        logger.info(f"{len(eczane_verileri)} adet eczane verisi çekildi.")
        
        # Veritabanına kaydet
        save_to_database(eczane_verileri)
        
        logger.info("Veri çekme ve kaydetme işlemi tamamlandı.")
        
    except Exception as e:
        logger.error(f"Veri çekme ve kaydetme sırasında hata oluştu: {str(e)}")
        logger.error(traceback.format_exc())


from app.utils.geocode import geocode_address

def save_to_database(eczane_verileri: List[ScraperEczane]):
    """
    Çekilen eczane verilerini veritabanına kaydeder.
    """
    db = SessionLocal()
    try:
        bugun = datetime.date.today()
        logger.info(f"Bugünün tarihi: {bugun}")
        
        for eczane_veri in eczane_verileri:
            # Eczane kaydını bul veya oluştur
            eczane = db.query(EczaneModel).filter(EczaneModel.isim == eczane_veri.isim).first()
            
            # Koordinatları al (eğer eczane_veri'de yoksa ve adres varsa)
            koordinatlar = None
            if not eczane_veri.latitude or not eczane_veri.longitude:
                # Önce konum URL'sinden koordinat çıkarmayı dene
                if eczane_veri.konum_url:
                    from app.utils.geocode import get_coordinates_from_google_maps_url
                    koordinatlar = get_coordinates_from_google_maps_url(eczane_veri.konum_url)
                    if koordinatlar:
                        logger.info(f"{eczane_veri.isim} için konum URL'sinden koordinatlar çıkarıldı: {koordinatlar}")
                
                # Konum URL'sinden çıkarılamazsa, adresten geocoding dene
                if not koordinatlar and eczane_veri.adres:
                    logger.info(f"{eczane_veri.isim} için adresle geocoding deneniyor...")
                    koordinatlar = geocode_address(eczane_veri.adres)
                    
                if koordinatlar:
                    eczane_veri.latitude, eczane_veri.longitude = koordinatlar
                    logger.info(f"Koordinatlar alındı: ({eczane_veri.latitude}, {eczane_veri.longitude})")
                else:
                    logger.warning(f"{eczane_veri.isim} için koordinatlar bulunamadı")
            
            if not eczane:
                # Yeni eczane oluştur
                eczane = EczaneModel(
                    bolge=eczane_veri.bolge,
                    isim=eczane_veri.isim,
                    konum_url=eczane_veri.konum_url,
                    adres=eczane_veri.adres,
                    telefon=eczane_veri.telefon,
                    latitude=eczane_veri.latitude,
                    longitude=eczane_veri.longitude
                )
                db.add(eczane)
                db.commit()
                db.refresh(eczane)
                logger.info(f"Yeni eczane kaydı oluşturuldu: {eczane.isim}")
            else:
                # Mevcut eczane bilgilerini güncelle
                eczane.bolge = eczane_veri.bolge
                eczane.konum_url = eczane_veri.konum_url
                eczane.adres = eczane_veri.adres
                eczane.telefon = eczane_veri.telefon
                
                # Koordinatları güncelle (eğer yeni koordinatlar varsa)
                if eczane_veri.latitude and eczane_veri.longitude:
                    eczane.latitude = eczane_veri.latitude
                    eczane.longitude = eczane_veri.longitude
                
                db.commit()
                logger.info(f"Mevcut eczane bilgileri güncellendi: {eczane.isim}")
            
            # Bugünün nöbetçi kaydını kontrol et
            nobetci = db.query(NobetciEczaneModel).filter(
                NobetciEczaneModel.eczane_id == eczane.id,
                NobetciEczaneModel.tarih == bugun
            ).first()
            
            if not nobetci:
                # Yeni nöbetçi kaydı oluştur
                nobetci = NobetciEczaneModel(
                    eczane_id=eczane.id,
                    tarih=bugun,
                    not_bilgisi=eczane_veri.not_bilgisi
                )
                db.add(nobetci)
                db.commit()
                logger.info(f"Yeni nöbetçi eczane kaydı oluşturuldu: {eczane.isim} - {bugun}")
            else:
                # Not bilgisini güncelle
                nobetci.not_bilgisi = eczane_veri.not_bilgisi
                db.commit()
                logger.info(f"Nöbetçi eczane not bilgisi güncellendi: {eczane.isim} - {bugun}")
                
    except Exception as e:
        db.rollback()
        logger.error(f"Veritabanına kaydetme sırasında hata oluştu: {str(e)}")
        logger.error(traceback.format_exc())
        raise
    finally:
        db.close()