
import requests
from dotenv import load_dotenv
import os

load_dotenv()

OPENCAGE_KEY = os.getenv("OPENCAGE_KEY")
OPENWEATHER_KEY = os.getenv("OPENWEATHER_KEY")
PEXELS_KEY = os.getenv("PEXELS_KEY")

# ----------------------------
# API 1 – GEOCODING
# ----------------------------

def get_coordinates(city):
    url = "https://api.opencagedata.com/geocode/v1/json"
    params = {"q": city, "key": OPENCAGE_KEY, "limit": 1}
    data = requests.get(url, params=params).json()

    if not data["results"]:
        return None

    result = data["results"][0]

    return {
        "lat": result["geometry"]["lat"],
        "lon": result["geometry"]["lng"],
        "country_code": result["components"]["country_code"].upper()
    }


# ----------------------------
# API 2 – WEATHER
# ----------------------------

def get_weather(lat=None, lon=None, city=None):
    url = "https://api.openweathermap.org/data/2.5/weather"

    if city:
        params = {"q": city, "appid": OPENWEATHER_KEY, "units": "metric"}
    else:
        params = {"lat": lat, "lon": lon, "appid": OPENWEATHER_KEY, "units": "metric"}

    data = requests.get(url, params=params).json()

    return {
        "temperature": data["main"]["temp"],
        "description": data["weather"][0]["description"]
    }


# ----------------------------
# API 3 – AIR QUALITY
# ----------------------------

def get_air_quality(lat, lon):
    url = "https://air-quality-api.open-meteo.com/v1/air-quality"
    params = {"latitude": lat, "longitude": lon, "hourly": "pm2_5"}
    data = requests.get(url, params=params).json()

    return {"pm25": data["hourly"]["pm2_5"][0]}


# ----------------------------
# API 4 – COUNTRY INFO
# ----------------------------

def get_country_info(code):
    url = f"https://restcountries.com/v3.1/alpha/{code}"
    data = requests.get(url).json()[0]

    return {
        "capital": data.get("capital", ["N/A"])[0],
        "population": data["population"],
        "currency": list(data["currencies"].keys())[0]
    }


# ----------------------------
# API 5 – IMAGE
# ----------------------------

def get_city_image(city):
    url = "https://api.pexels.com/v1/search"
    headers = {"Authorization": PEXELS_KEY}
    params = {"query": city, "per_page": 1}

    data = requests.get(url, headers=headers, params=params).json()

    if data.get("photos"):
        return data["photos"][0]["src"]["large"]

    return None


# ----------------------------
# SCORE CALCULATION
# ----------------------------

def calculate_scores(temp, pm25, population):

    comfort = max(0, 30 - abs(temp - 22))
    air_quality = max(0, 100 - pm25)
    density = max(0, 50 - (population / 2_000_000))

    total = comfort * 0.4 + air_quality * 0.4 + density * 0.2

    return {
        "comfort": round(comfort, 2),
        "air_quality": round(air_quality, 2),
        "density": round(density, 2),
        "total": round(total, 2)
    }


# ----------------------------
# BUILD BUNDLE (CITY + CAPITAL)
# ----------------------------

def build_city_bundle(city_name):

    coords = get_coordinates(city_name)
    if not coords:
        return None

    country = get_country_info(coords["country_code"])

    # CITY RAW
    city_weather = get_weather(lat=coords["lat"], lon=coords["lon"])
    city_air = get_air_quality(coords["lat"], coords["lon"])
    city_image = get_city_image(city_name)

    city_scores = calculate_scores(
        city_weather["temperature"],
        city_air["pm25"],
        country["population"]
    )

    city_data = {
        "raw": {
            "lat": coords["lat"],
            "lon": coords["lon"],
            "country_code": coords["country_code"],
            "temperature": city_weather["temperature"],
            "pm25": city_air["pm25"],
            "population": country["population"]
        },
        "processed": city_scores,
        "meta": {
            "name": city_name,
            "currency": country["currency"],
            "image": city_image
        }
    }

    # CAPITAL RAW (cascadare)
    capital_weather = get_weather(city=country["capital"])
    capital_image = get_city_image(country["capital"])

    capital_scores = calculate_scores(
        capital_weather["temperature"],
        city_air["pm25"],
        country["population"]
    )

    capital_data = {
        "raw": {
            "name": country["capital"],
            "temperature": capital_weather["temperature"],
            "population": country["population"]
        },
        "processed": capital_scores,
        "meta": {
            "image": capital_image
        }
    }

    return {
        "city": city_data,
        "capital": capital_data
    }


# ----------------------------
# COMPARISON
# ----------------------------

def compare_bundles(b1, b2):

    city_winner = (
        b1["city"]["meta"]["name"]
        if b1["city"]["processed"]["total"] >
           b2["city"]["processed"]["total"]
        else b2["city"]["meta"]["name"]
    )

    capital_winner = (
        b1["capital"]["raw"]["name"]
        if b1["capital"]["processed"]["total"] >
           b2["capital"]["processed"]["total"]
        else b2["capital"]["raw"]["name"]
    )

    return {
        "city_winner": city_winner,
        "capital_winner": capital_winner
    }