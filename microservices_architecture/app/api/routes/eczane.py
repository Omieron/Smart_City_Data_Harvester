"""
Eczane ile ilgili endpoint'ler.
"""
import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.database.models import Eczane as EczaneModel, NobetciEczane as NobetciEczaneModel
from app.database.schemas import Eczane as EczaneSchema, NobetciEczaneDetay
from app.utils.geocode import geocode_address

router = APIRouter()

@router.get("/eczaneler", response_model=List[EczaneSchema])
def get_all_eczaneler(
    skip: int = Query(0, description="Atlanacak öğe sayısı"),
    limit: int = Query(100, description="Listelenecek öğe sayısı"),
    db: Session = Depends(get_db)
):
    """
    Tüm eczaneleri listeler.
    """
    eczaneler = db.query(EczaneModel).offset(skip).limit(limit).all()
    return eczaneler

@router.get("/eczaneler/{eczane_id}", response_model=EczaneSchema)
def get_eczane(eczane_id: int, db: Session = Depends(get_db)):
    """
    Belirtilen ID'ye sahip eczaneyi getirir.
    """
    eczane = db.query(EczaneModel).filter(EczaneModel.id == eczane_id).first()
    if eczane is None:
        raise HTTPException(status_code=404, detail="Eczane bulunamadı")
    return eczane

@router.get("/eczaneler/koordinat/{eczane_id}")
def get_eczane_koordinat(eczane_id: int, db: Session = Depends(get_db)):
    """
    Belirtilen ID'ye sahip eczanenin koordinat bilgilerini getirir.
    """
    eczane = db.query(EczaneModel).filter(EczaneModel.id == eczane_id).first()
    if eczane is None:
        raise HTTPException(status_code=404, detail="Eczane bulunamadı")
    
    if eczane.latitude is None or eczane.longitude is None:
        return {
            "id": eczane.id,
            "isim": eczane.isim,
            "koordinat_durumu": "bulunamadı"
        }
    
    return {
        "id": eczane.id,
        "isim": eczane.isim,
        "latitude": eczane.latitude,
        "longitude": eczane.longitude,
        "koordinat_durumu": "başarılı"
    }

@router.get("/nobetci-eczaneler", response_model=List[NobetciEczaneDetay])
def get_nobetci_eczaneler(
    tarih: Optional[datetime.date] = Query(None, description="Nöbet tarihi (YYYY-MM-DD formatında)"),
    bolge: Optional[str] = Query(None, description="Bölge adı"),
    koordinat: Optional[bool] = Query(False, description="Koordinat bilgisi olan eczaneleri filtrele"),
    db: Session = Depends(get_db)
):
    """
    Belirtilen tarihteki nöbetçi eczaneleri listeler.
    Tarih belirtilmezse, bugünün nöbetçi eczaneleri listelenir.
    İsteğe bağlı olarak bölge filtrelemesi de yapılabilir.
    """
    # Tarih belirtilmemişse bugünün tarihini kullan
    if tarih is None:
        tarih = datetime.date.today()
    
    # Nöbetçi eczaneleri sorgula
    query = db.query(NobetciEczaneModel).filter(NobetciEczaneModel.tarih == tarih)
    
    # Eczane bilgilerini eager loading ile birlikte getir
    query = query.options(joinedload(NobetciEczaneModel.eczane))
    
    # Join ile eczane tablosunu birleştir
    query = query.join(EczaneModel)
    
    # Bölge filtresi uygulandıysa sorguya ekle
    if bolge:
        query = query.filter(EczaneModel.bolge == bolge)
    
    # Koordinat filtresi uygulandıysa sorguya ekle
    if koordinat:
        query = query.filter(EczaneModel.latitude.isnot(None), EczaneModel.longitude.isnot(None))
    
    # Sorguyu çalıştır
    nobetci_eczaneler = query.all()
    
    return nobetci_eczaneler

@router.get("/tarihler", response_model=List[datetime.date])
def get_nobetci_tarihler(
    baslangic: Optional[datetime.date] = Query(None, description="Başlangıç tarihi (YYYY-MM-DD formatında)"),
    bitis: Optional[datetime.date] = Query(None, description="Bitiş tarihi (YYYY-MM-DD formatında)"),
    db: Session = Depends(get_db)
):
    """
    Nöbetçi eczane kayıtlarının bulunduğu tarihleri listeler.
    İsteğe bağlı olarak başlangıç ve bitiş tarihi belirtilebilir.
    """
    # Tarihleri veritabanından çek
    query = db.query(NobetciEczaneModel.tarih).distinct()
    
    # Başlangıç tarihi belirtilmişse filtrele
    if baslangic:
        query = query.filter(NobetciEczaneModel.tarih >= baslangic)
    
    # Bitiş tarihi belirtilmişse filtrele
    if bitis:
        query = query.filter(NobetciEczaneModel.tarih <= bitis)
    
    # Tarihleri sırala (en yakın tarih en üstte)
    query = query.order_by(NobetciEczaneModel.tarih.desc())
    
    # Sorguyu çalıştır ve tarihleri liste olarak döndür
    tarihler = [tarih[0] for tarih in query.all()]
    
    return tarihler

@router.get("/bolgeler", response_model=List[str])
def get_bolgeler(db: Session = Depends(get_db)):
    """
    Sistemde kayıtlı tüm bölgeleri listeler.
    """
    # Bölgeleri veritabanından çek (benzersiz)
    bolgeler = db.query(EczaneModel.bolge).distinct().all()
    
    # Bölge adlarını liste olarak döndür
    return [bolge[0] for bolge in bolgeler]

@router.get("/eczaneler/harita-bilgileri")
def get_eczaneler_harita_bilgileri(
    sadece_nobetci: bool = Query(False, description="Sadece bugünün nöbetçi eczanelerini göster"),
    db: Session = Depends(get_db)
):
    return

@router.post("/eczaneler/{eczane_id}/koordinat-guncelle")
def update_eczane_koordinat(
    eczane_id: int, 
    latitude: float = Query(..., description="Enlem değeri"),
    longitude: float = Query(..., description="Boylam değeri"),
    db: Session = Depends(get_db)
):
    """
    Belirtilen ID'ye sahip eczanenin koordinat bilgilerini günceller.
    """
    eczane = db.query(EczaneModel).filter(EczaneModel.id == eczane_id).first()
    if eczane is None:
        raise HTTPException(status_code=404, detail="Eczane bulunamadı")
    
    # Koordinatları güncelle
    eczane.latitude = latitude
    eczane.longitude = longitude
    
    try:
        db.commit()
        return {
            "id": eczane.id,
            "isim": eczane.isim,
            "latitude": eczane.latitude,
            "longitude": eczane.longitude,
            "mesaj": "Koordinat bilgileri başarıyla güncellendi"
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Güncelleme hatası: {str(e)}")

@router.post("/eczaneler/{eczane_id}/adresle-koordinat-bul")
def find_koordinat_by_address(
    eczane_id: int,
    db: Session = Depends(get_db)
):
    """
    Belirtilen ID'ye sahip eczanenin adresini kullanarak koordinat bilgilerini bulur ve günceller.
    """
    eczane = db.query(EczaneModel).filter(EczaneModel.id == eczane_id).first()
    if eczane is None:
        raise HTTPException(status_code=404, detail="Eczane bulunamadı")
    
    if not eczane.adres:
        raise HTTPException(status_code=400, detail="Eczanenin adresi bulunmamaktadır")
    
    # Koordinatları bul
    koordinatlar = geocode_address(eczane.adres)
    
    if not koordinatlar:
        # Adres ile bulunamazsa, konum URL'sini dene
        if eczane.konum_url:
            from app.utils.geocode import get_coordinates_from_google_maps_url
            koordinatlar = get_coordinates_from_google_maps_url(eczane.konum_url)
    
    if not koordinatlar:
        raise HTTPException(status_code=404, detail=f"Adrese ait koordinat bulunamadı: {eczane.adres}")
    
    # Koordinatları güncelle
    eczane.latitude, eczane.longitude = koordinatlar
    
    try:
        db.commit()
        return {
            "id": eczane.id,
            "isim": eczane.isim,
            "adres": eczane.adres,
            "latitude": eczane.latitude,
            "longitude": eczane.longitude,
            "mesaj": "Koordinat bilgileri başarıyla güncellendi"
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Güncelleme hatası: {str(e)}")

@router.get("/eczaneler/harita-bilgileri")
def get_eczaneler_harita_bilgileri(
    sadece_nobetci: bool = Query(False, description="Sadece bugünün nöbetçi eczanelerini göster"),
    db: Session = Depends(get_db)
):
    """
    Haritada gösterilecek eczane koordinat bilgilerini döndürür.
    Sadece koordinat bilgisi olan eczaneleri içerir.
    """
    query = db.query(
        EczaneModel.id,
        EczaneModel.isim,
        EczaneModel.bolge,
        EczaneModel.adres,
        EczaneModel.telefon,
        EczaneModel.latitude,
        EczaneModel.longitude
    ).filter(
        EczaneModel.latitude.isnot(None),
        EczaneModel.longitude.isnot(None)
    )
    
    # Sadece bugünün nöbetçi eczanelerini istiyorsa filtrele
    if sadece_nobetci:
        bugun = datetime.date.today()
        query = query.join(NobetciEczaneModel).filter(NobetciEczaneModel.tarih == bugun)
    
    eczaneler = query.all()
    
    # Sonuçları uygun formatta döndür
    sonuc = []
    for e in eczaneler:
        sonuc.append({
            "id": e.id,
            "isim": e.isim,
            "bolge": e.bolge,
            "adres": e.adres,
            "telefon": e.telefon,
            "latitude": e.latitude,
            "longitude": e.longitude,
            "nobetci": sadece_nobetci  # Eğer sadece_nobetci=True ise, tüm sonuçlar nöbetçidir
        })
    
    return sonuc