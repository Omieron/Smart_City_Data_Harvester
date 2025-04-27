"""
HTML parsing işlemleri.
"""
import requests
from typing import List, Optional
from bs4 import BeautifulSoup
from loguru import logger

from app.database.schemas import ScraperEczane

def parse_eczane_data(url: str) -> List[ScraperEczane]:
    """
    Web sayfasından eczane verilerini çeker ve analiz eder.
    
    Args:
        url: Çekilecek web sayfasının URL'i
        
    Returns:
        List[ScraperEczane]: Çekilen eczane verilerinin listesi
    """
    try:
        # Web sayfasını indir
        response = requests.get(url)
        response.raise_for_status()
        
        # HTML içeriğini analiz et
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Eczane bilgilerini içeren div'leri bul
        eczane_divleri = soup.select('div.itemwrap[style*="display: block"]')
        
        eczaneler = []
        
        for div in eczane_divleri:
            try:
                # Bölge bilgisini al
                bolge_div = div.select_one('div.tag.discount')
                bolge = bolge_div.text.strip() if bolge_div else "Bilinmiyor"
                
                # Eczane adını al
                isim_div = div.select_one('div.itemwrap_title')
                isim = isim_div.text.strip() if isim_div else "Bilinmiyor"
                
                # Konum URL'sini al
                konum_a = div.select_one('a[href*="maps"]')
                konum_url = konum_a['href'] if konum_a else ""
                
                # Adres bilgisini al
                adres_element = div.find_all('div', class_='itemwrap_position')
                adres = ""
                if adres_element and len(adres_element) > 0:
                    for element in adres_element:
                        fa_marker = element.find('i', class_='fa-map-marker')
                        if fa_marker and fa_marker.parent:
                            # i elementinin parent elementinin text içeriğini al
                            adres = fa_marker.parent.get_text().strip()
                            # fa-map-marker icon'unu içermeyecek şekilde metni düzenle
                            adres = adres.replace('\n', ' ').strip()
                            break
                
                # Telefon bilgisini al
                telefon_a = div.select_one('div.itemwrap_position a[href*="tel:"]')
                telefon = telefon_a.text.strip() if telefon_a else "Bilinmiyor"
                
                # Ek not bilgisi var mı kontrol et (örn: "Saat 20.00'a kadar nöbetçidir.")
                not_div = div.select_one('div[style*="font-size: smaller"]')
                not_bilgisi = not_div.text.strip() if not_div else ""
                
                # Google Maps URL'sinden koordinatları çıkarmaya çalış
                lat, lon = None, None
                if konum_url and "maps" in konum_url:
                    try:
                        from app.utils.geocode import get_coordinates_from_google_maps_url
                        
                        coords = get_coordinates_from_google_maps_url(konum_url)
                        if coords:
                            lat, lon = coords
                            logger.debug(f"URL'den koordinatlar çıkarıldı: ({lat}, {lon})")
                        else:
                            logger.debug(f"URL'den koordinat çıkarılamadı: {konum_url}")
                    except Exception as e:
                        logger.warning(f"URL'den koordinat çıkarma hatası: {str(e)}")
                
                eczane = ScraperEczane(
                    bolge=bolge,
                    isim=isim,
                    konum_url=konum_url,
                    adres=adres,
                    telefon=telefon,
                    not_bilgisi=not_bilgisi,
                    latitude=lat,
                    longitude=lon
                )
                
                eczaneler.append(eczane)
                logger.debug(f"Eczane bilgisi çekildi: {isim}")
                
            except Exception as e:
                logger.error(f"Eczane bilgisi çekilirken hata: {str(e)}")
        
        return eczaneler
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Web sayfasına erişilemiyor: {str(e)}")
        return []
    
    except Exception as e:
        logger.error(f"Veri çekme sırasında hata oluştu: {str(e)}")
        return []