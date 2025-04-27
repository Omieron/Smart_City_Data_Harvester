"""
Veritabanı modelleri.
"""
import datetime
import sys
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Date, Float, UniqueConstraint, create_engine
from sqlalchemy.orm import relationship
from app.database.connection import Base, engine
from loguru import logger

class Eczane(Base):
    """Eczane tablosu."""
    
    __tablename__ = "eczaneler"
    
    id = Column(Integer, primary_key=True, index=True)
    bolge = Column(String(100), nullable=False)
    isim = Column(String(150), nullable=False, unique=True)
    konum_url = Column(Text)
    adres = Column(Text)
    telefon = Column(String(20))
    latitude = Column(Float, nullable=True)  # Koordinat (enlem)
    longitude = Column(Float, nullable=True)  # Koordinat (boylam)
    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)
    
    # İlişki
    nobetler = relationship("NobetciEczane", back_populates="eczane")
    
    def __repr__(self):
        return f"<Eczane(id={self.id}, isim='{self.isim}')>"


class NobetciEczane(Base):
    """Nöbetçi Eczane tablosu."""
    
    __tablename__ = "nobetci_eczaneler"
    
    id = Column(Integer, primary_key=True, index=True)
    eczane_id = Column(Integer, ForeignKey("eczaneler.id"), nullable=False)
    tarih = Column(Date, nullable=False)
    not_bilgisi = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.now)
    
    # İlişki
    eczane = relationship("Eczane", back_populates="nobetler")
    
    __table_args__ = (
        UniqueConstraint('eczane_id', 'tarih', name='unique_eczane_tarih'),
    )
    
    def __repr__(self):
        return f"<NobetciEczane(id={self.id}, tarih='{self.tarih}', eczane_id={self.eczane_id})>"


def create_tables():
    """
    Veritabanı tablolarını oluşturan fonksiyon.
    Bu fonksiyon, veritabanında tanımlanan tüm modeller için tablolar oluşturur.
    """
    try:
        logger.info("Veritabanı tabloları oluşturuluyor...")
        Base.metadata.create_all(bind=engine)
        logger.info("Veritabanı tabloları başarıyla oluşturuldu.")
    except Exception as e:
        logger.error(f"Veritabanı tabloları oluşturulurken hata: {str(e)}")
        return False
    return True


# Bu modül doğrudan çalıştırıldığında tabloları oluştur
if __name__ == "__main__":
    success = create_tables()
    sys.exit(0 if success else 1)