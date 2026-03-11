import requests
import os
from dotenv import load_dotenv

load_dotenv()

# Cheile API (luate din .env)
CHEIE_OPENCAGE = os.getenv("OPENCAGE_KEY")
CHEIE_VREME = os.getenv("OPENWEATHER_KEY")
CHEIE_PEXELS = os.getenv("PEXELS_KEY")


# -------------------------------------------------
# 1️⃣ FUNCȚIE: Obține coordonatele unui oraș
# -------------------------------------------------
def obtine_coordonate(nume_oras):

    url = "https://api.opencagedata.com/geocode/v1/json"
    parametri = {
        "q": nume_oras,
        "key": CHEIE_OPENCAGE,
        "limit": 1
    }

    raspuns = requests.get(url, params=parametri).json()

    if not raspuns["results"]:
        return None

    rezultat = raspuns["results"][0]

    return {
        "lat": rezultat["geometry"]["lat"],
        "lon": rezultat["geometry"]["lng"],
        "cod_tara": rezultat["components"]["country_code"].upper()
    }


# -------------------------------------------------
# 2️⃣ FUNCȚIE: Obține vremea
# -------------------------------------------------
def obtine_vreme(lat=None, lon=None, oras=None):

    url = "https://api.openweathermap.org/data/2.5/weather"

    if oras:
        parametri = {
            "q": oras,
            "appid": CHEIE_VREME,
            "units": "metric"
        }
    else:
        parametri = {
            "lat": lat,
            "lon": lon,
            "appid": CHEIE_VREME,
            "units": "metric"
        }

    raspuns = requests.get(url, params=parametri).json()

    return {
        "temperatura": raspuns["main"]["temp"],
        "descriere": raspuns["weather"][0]["description"]
    }


# -------------------------------------------------
# 3️⃣ FUNCȚIE: Obține calitatea aerului
# -------------------------------------------------
def obtine_calitate_aer(lat, lon):

    url = "https://air-quality-api.open-meteo.com/v1/air-quality"
    parametri = {
        "latitude": lat,
        "longitude": lon,
        "hourly": "pm2_5"
    }

    raspuns = requests.get(url, params=parametri).json()

    return {
        "pm25": raspuns["hourly"]["pm2_5"][0]
    }


# -------------------------------------------------
# 4️⃣ FUNCȚIE: Obține informații despre țară
# -------------------------------------------------
def obtine_informatii_tara(cod_tara):

    url = f"https://restcountries.com/v3.1/alpha/{cod_tara}"
    raspuns = requests.get(url).json()[0]

    return {
        "capitala": raspuns.get("capital", ["N/A"])[0],
        "populatie": raspuns["population"],
        "moneda": list(raspuns["currencies"].keys())[0]
    }


# -------------------------------------------------
# 5️⃣ FUNCȚIE: Obține imagine
# -------------------------------------------------
def obtine_imagine(nume_oras):

    url = "https://api.pexels.com/v1/search"

    header = {"Authorization": CHEIE_PEXELS}
    parametri = {"query": nume_oras, "per_page": 1}

    raspuns = requests.get(url, headers=header, params=parametri).json()

    if raspuns.get("photos"):
        return raspuns["photos"][0]["src"]["large"]

    return None


# -------------------------------------------------
# 6️⃣ FUNCȚIE: Calculează scorurile
# -------------------------------------------------
def calculeaza_scoruri(temperatura, pm25, populatie):

    # Scor confort – ideal 22°C
    scor_confort = max(0, 30 - abs(temperatura - 22))

    # Scor calitate aer – poluare mică = scor mare
    scor_aer = max(0, 100 - pm25)

    # Scor densitate – populație mare = penalizare
    scor_densitate = max(0, 50 - (populatie / 2_000_000))

    # Scor total ponderat
    scor_total = (
        scor_confort * 0.4 +
        scor_aer * 0.4 +
        scor_densitate * 0.2
    )

    return {
        "confort": round(scor_confort, 2),
        "aer": round(scor_aer, 2),
        "densitate": round(scor_densitate, 2),
        "total": round(scor_total, 2)
    }