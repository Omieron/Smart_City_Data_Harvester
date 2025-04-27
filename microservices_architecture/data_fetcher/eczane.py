from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import requests
from bs4 import BeautifulSoup
from typing import List
from pydantic import BaseModel

class Eczane(BaseModel):
    bolge: str
    isim: str
    konum_url: str
    adres: str
    telefon: str
    not_bilgisi: str = ""  # Bazı eczanelerde görülen saat notu gibi ek bilgiler için

app = FastAPI(title="Edremit Nöbetçi Eczane API")

# CORS ayarları
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def ana_sayfa():
    return {"mesaj": "Edremit Nöbetçi Eczane API'sine hoş geldiniz. /eczaneler endpoint'ini kullanabilirsiniz."}

@app.get("/eczaneler", response_model=List[Eczane])
def get_eczaneler():
    try:
        # Web sayfasını indirme
        url = "https://www.edremit.bel.tr/Guncel/NobetciE/"
        response = requests.get(url)
        response.raise_for_status()
        
        # HTML içeriğini parse etme
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Eczane bilgilerini içeren div'leri bulma
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
                
                # Konum URL'sini al - DÜZELTME BURADA
                konum_a = div.select_one('a[href*="maps"]')  # Bütün map linklerini kapsayacak şekilde
                konum_url = konum_a['href'] if konum_a else ""
                
                # Adres bilgisini al
                adres_element = div.find_all('div', class_='itemwrap_position')
                adres = ""
                if adres_element and len(adres_element) > 0:
                    for element in adres_element:
                        fa_marker = element.find('i', class_='fa-map-marker')
                        if fa_marker:
                            adres = fa_marker.get_text().strip()
                            break
                
                # Telefon bilgisini al
                telefon_a = div.select_one('div.itemwrap_position a[href*="tel:"]')
                telefon = telefon_a.text.strip() if telefon_a else "Bilinmiyor"
                
                # Ek not bilgisi var mı kontrol et (örn: "Saat 20.00'a kadar nöbetçidir.")
                not_div = div.select_one('div[style*="font-size: smaller"]')
                not_bilgisi = not_div.text.strip() if not_div else ""
                
                eczane = Eczane(
                    bolge=bolge,
                    isim=isim,
                    konum_url=konum_url,
                    adres=adres,
                    telefon=telefon,
                    not_bilgisi=not_bilgisi
                )
                
                eczaneler.append(eczane)
                
            except Exception as e:
                print(f"Eczane bilgisi çekilirken hata: {str(e)}")
        
        return eczaneler
        
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=503, detail=f"Web sayfasına erişilemiyor: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Bir hata oluştu: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)