"""
Pydantic modelleri (API şemaları).
"""
import datetime
from typing import List, Optional
from pydantic import BaseModel

# Eczane şemaları
class EczaneBase(BaseModel):
    """Temel Eczane şeması."""
    bolge: str
    isim: str
    konum_url: Optional[str] = None
    adres: Optional[str] = None
    telefon: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class EczaneCreate(EczaneBase):
    """Eczane oluşturma şeması."""
    pass


class EczaneUpdate(EczaneBase):
    """Eczane güncelleme şeması."""
    bolge: Optional[str] = None
    isim: Optional[str] = None


class Eczane(EczaneBase):
    """Eczane yanıt şeması."""
    id: int
    created_at: datetime.datetime
    updated_at: datetime.datetime
    
    class Config:
        orm_mode = True


# Nöbetçi Eczane şemaları
class NobetciEczaneBase(BaseModel):
    """Temel Nöbetçi Eczane şeması."""
    eczane_id: int
    tarih: datetime.date
    not_bilgisi: Optional[str] = None


class NobetciEczaneCreate(NobetciEczaneBase):
    """Nöbetçi Eczane oluşturma şeması."""
    pass


class NobetciEczane(NobetciEczaneBase):
    """Nöbetçi Eczane yanıt şeması."""
    id: int
    created_at: datetime.datetime
    
    class Config:
        orm_mode = True


# Birleştirilmiş nöbetçi eczane şeması
class NobetciEczaneDetay(BaseModel):
    """Detaylı Nöbetçi Eczane bilgisi."""
    id: int
    tarih: datetime.date
    not_bilgisi: Optional[str] = None
    eczane: Eczane
    
    class Config:
        orm_mode = True


# Web scraper için şema
class ScraperEczane(BaseModel):
    """Web scraper'dan gelen eczane bilgisi şeması."""
    bolge: str
    isim: str
    konum_url: str
    adres: str
    telefon: str
    not_bilgisi: Optional[str] = ""
    latitude: Optional[float] = None
    longitude: Optional[float] = None