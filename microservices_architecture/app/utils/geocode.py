"""
Adres - koordinat dönüşüm işlemleri.
"""
import requests
import time
from typing import Tuple, Optional
from loguru import logger
from geopy.geocoders import Nominatim

def geocode_address(address: str, city: str = "Edremit", country: str = "Turkey") -> Optional[Tuple[float, float]]:
    """
    Adresi koordinatlara (enlem, boylam) çevirir.
    Önce Geopy kütüphanesi ile dener, başarısız olursa doğrudan Nominatim API'ye istek yapar.
    
    Args:
        address: Koordinatları alınacak adres
        city: Şehir adı (varsayılan: Edremit)
        country: Ülke adı (varsayılan: Turkey)
        
    Returns:
        Tuple[float, float]: (enlem, boylam) koordinat çifti, adres çözülemezse None
    """
    if not address:
        logger.warning("Geocode için adres boş")
        return None
    
    # Adres hazırla
    full_address = f"{address}, {city}, {country}"
    
    # Yöntem 1: Geopy kütüphanesi ile
    try:
        geolocator = Nominatim(user_agent="EdremitEczaneAPI/1.0")
        location = geolocator.geocode(full_address, timeout=10)
        
        if location:
            logger.info(f"Geopy ile geocode başarılı: {full_address} -> ({location.latitude}, {location.longitude})")
            return (location.latitude, location.longitude)
        else:
            logger.warning(f"Geopy ile koordinat bulunamadı: {full_address}")
    except Exception as e:
        logger.error(f"Geopy ile geocode işlemi hatası: {str(e)}")
    
    # Yöntem 2: Doğrudan Nominatim API çağrısı
    try:
        # API rate limit - saniyede 1 istekten fazla yapmamak için
        time.sleep(1)
        
        # Nominatim API için parametreler
        params = {
            'q': full_address,
            'format': 'json',
            'limit': 1,
            'addressdetails': 1
        }
        
        # API isteği
        response = requests.get('https://nominatim.openstreetmap.org/search', params=params, 
                                headers={'User-Agent': 'EdremitEczaneAPI/1.0'})
        
        if response.status_code != 200:
            logger.error(f"Geocode API hatası: {response.status_code}")
            return None
        
        data = response.json()
        
        if not data:
            logger.warning(f"API ile koordinat bulunamadı: {full_address}")
            return None
        
        # İlk sonucu al
        location = data[0]
        lat = float(location['lat'])
        lon = float(location['lon'])
        
        logger.info(f"API ile geocode başarılı: {full_address} -> ({lat}, {lon})")
        return (lat, lon)
        
    except Exception as e:
        logger.error(f"API ile geocode işlemi hatası: {str(e)}")
        return None


def reverse_geocode(lat: float, lon: float) -> Optional[str]:
    """
    Koordinatları adrese çevirir.
    Önce Geopy ile dener, başarısız olursa Nominatim API'ye doğrudan istek yapar.
    
    Args:
        lat: Enlem
        lon: Boylam
        
    Returns:
        str: Adres bilgisi, çözülemezse None
    """
    if not lat or not lon:
        logger.warning("Reverse geocode için koordinatlar eksik")
        return None
    
    # Yöntem 1: Geopy kütüphanesi ile
    try:
        geolocator = Nominatim(user_agent="EdremitEczaneAPI/1.0")
        location = geolocator.reverse((lat, lon), timeout=10)
        
        if location:
            address = location.address
            logger.info(f"Geopy ile reverse geocode başarılı: ({lat}, {lon}) -> {address}")
            return address
        else:
            logger.warning(f"Geopy ile adres bulunamadı: ({lat}, {lon})")
    except Exception as e:
        logger.error(f"Geopy ile reverse geocode işlemi hatası: {str(e)}")
    
    # Yöntem 2: Doğrudan Nominatim API çağrısı
    try:
        # API rate limit - saniyede 1 istekten fazla yapmamak için
        time.sleep(1)
        
        # Nominatim API için parametreler
        params = {
            'lat': lat,
            'lon': lon,
            'format': 'json',
            'addressdetails': 1
        }
        
        # API isteği
        response = requests.get('https://nominatim.openstreetmap.org/reverse', params=params, 
                                headers={'User-Agent': 'EdremitEczaneAPI/1.0'})
        
        if response.status_code != 200:
            logger.error(f"Reverse geocode API hatası: {response.status_code}")
            return None
        
        data = response.json()
        
        if 'error' in data:
            logger.warning(f"API ile adres bulunamadı: ({lat}, {lon})")
            return None
        
        # Adresi al
        address = data.get('display_name', '')
        
        logger.info(f"API ile reverse geocode başarılı: ({lat}, {lon}) -> {address}")
        return address
        
    except Exception as e:
        logger.error(f"API ile reverse geocode işlemi hatası: {str(e)}")
        return None

def get_coordinates_from_google_maps_url(url: str) -> Optional[Tuple[float, float]]:
    """
    Google Maps URL'inden koordinat bilgilerini çıkarır.
    
    Args:
        url: Google Maps URL'i
        
    Returns:
        Tuple[float, float]: (enlem, boylam) koordinat çifti, çıkarılamazsa None
    """
    if not url:
        return None
    
    try:
        # Kısaltılmış goo.gl URL'lerini işle
        if "goo.gl" in url or "maps.app.goo.gl" in url:
            # Kısaltılmış URL'leri takip etmemiz gerekiyor
            try:
                logger.info(f"Kısaltılmış URL tespit edildi: {url}")
                response = requests.head(url, allow_redirects=True)
                if response.status_code == 200:
                    # Yönlendirilen URL'yi al
                    final_url = response.url
                    logger.info(f"URL yönlendirmesi: {final_url}")
                    
                    # Yönlendirilen URL'de koordinat kontrolü yap
                    if "/@" in final_url:
                        coords_part = final_url.split("/@")[1].split("/")[0]
                        coords = coords_part.split(",")
                        if len(coords) >= 2:
                            try:
                                lat = float(coords[0])
                                lon = float(coords[1])
                                logger.info(f"Kısaltılmış URL'den koordinatlar bulundu: ({lat}, {lon})")
                                return (lat, lon)
                            except ValueError:
                                logger.warning(f"Kısaltılmış URL'den geçersiz koordinatlar: {coords}")
            except Exception as e:
                logger.error(f"Kısaltılmış URL işleme hatası: {str(e)}")
            
            return None
                
        # Normal maps URL'leri için kontroller
        if "maps" not in url:
            return None
            
        # @lat,lon,zoom formatındaki URL'leri analiz et
        if "/@" in url:
            coords_part = url.split("/@")[1].split("/")[0]
            coords = coords_part.split(",")
            if len(coords) >= 2:
                try:
                    lat = float(coords[0])
                    lon = float(coords[1])
                    return (lat, lon)
                except ValueError:
                    logger.warning(f"URL'deki koordinat formatı geçersiz: {coords}")
                
        # ?q=lat,lon formatındaki URL'leri analiz et
        elif "?q=" in url:
            coords_part = url.split("?q=")[1].split("&")[0]
            if "," in coords_part:
                coords = coords_part.split(",")
                if len(coords) >= 2:
                    try:
                        lat = float(coords[0])
                        lon = float(coords[1])
                        return (lat, lon)
                    except ValueError:
                        # Koordinat değil, adres olabilir
                        pass
                        
        # place/lat,lon formatındaki URL'leri analiz et
        elif "/place/" in url:
            parts = url.split("/place/")[1].split("/@")
            if len(parts) > 1:
                coords_part = parts[1].split(",")
                if len(coords_part) >= 2:
                    try:
                        lat = float(coords_part[0])
                        lon = float(coords_part[1])
                        return (lat, lon)
                    except ValueError:
                        logger.warning(f"Place URL'deki koordinat formatı geçersiz: {coords_part}")
                    
        return None
    except Exception as e:
        logger.error(f"URL'den koordinat çıkarma hatası: {str(e)}")
        return None