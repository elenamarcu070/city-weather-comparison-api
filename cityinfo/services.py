
import requests
from dotenv import load_dotenv
import os

load_dotenv()

OPENCAGE_KEY = os.getenv("OPENCAGE_KEY")
OPENWEATHER_KEY = os.getenv("OPENWEATHER_KEY")
PEXELS_KEY = os.getenv("PEXELS_KEY")

# -----------------------
# GEOCODING
# -----------------------

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


# -----------------------
# WEATHER
# -----------------------

def get_weather(lat, lon):
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "lat": lat,
        "lon": lon,
        "appid": OPENWEATHER_KEY,
        "units": "metric"
    }

    data = requests.get(url, params=params).json()

    return {
        "temperature": data["main"]["temp"],
        "description": data["weather"][0]["description"]
    }


def get_weather_by_city(city_name):
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city_name,
        "appid": OPENWEATHER_KEY,
        "units": "metric"
    }

    data = requests.get(url, params=params).json()

    return {
        "temperature": data["main"]["temp"],
        "description": data["weather"][0]["description"]
    }


# -----------------------
# AIR QUALITY
# -----------------------

def get_air_quality(lat, lon):
    url = "https://air-quality-api.open-meteo.com/v1/air-quality"
    params = {"latitude": lat, "longitude": lon, "hourly": "pm2_5"}
    data = requests.get(url, params=params).json()

    return {"pm25": data["hourly"]["pm2_5"][0]}


# -----------------------
# COUNTRY INFO
# -----------------------

def get_country_info(code):
    url = f"https://restcountries.com/v3.1/alpha/{code}"
    data = requests.get(url).json()[0]

    return {
        "capital": data.get("capital", ["N/A"])[0],
        "population": data["population"],
        "currency": list(data["currencies"].keys())[0]
    }


# -----------------------
# IMAGE
# -----------------------

def get_city_image(city):
    url = "https://api.pexels.com/v1/search"

    headers = {"Authorization": PEXELS_KEY}
    params = {"query": city, "per_page": 1}

    data = requests.get(url, headers=headers, params=params).json()

    if data.get("photos"):
        return data["photos"][0]["src"]["large"]

    return None


# -----------------------
# SCORE SYSTEM
# -----------------------

def calculate_scores(temp, pm25, population):
    comfort = max(0, 30 - abs(temp - 22))
    air_score = max(0, 100 - pm25)
    density_score = max(0, 50 - (population / 2_000_000))

    total = comfort * 0.4 + air_score * 0.4 + density_score * 0.2

    return {
        "comfort": round(comfort, 2),
        "air_quality": round(air_score, 2),
        "density": round(density_score, 2),
        "total": round(total, 2)
    }


# -----------------------
# BUILD CITY + CAPITAL
# -----------------------

def build_city_bundle(city_name):

    coords = get_coordinates(city_name)
    if not coords:
        return None

    # ---- CITY ----
    weather = get_weather(coords["lat"], coords["lon"])
    air = get_air_quality(coords["lat"], coords["lon"])
    country = get_country_info(coords["country_code"])
    image = get_city_image(city_name)

    city_scores = calculate_scores(
        weather["temperature"],
        air["pm25"],
        country["population"]
    )

    city_data = {
        "name": city_name,
        "temperature": weather["temperature"],
        "description": weather["description"],
        "pm25": air["pm25"],
        "population": country["population"],
        "currency": country["currency"],
        "image": image,
        "scores": city_scores
    }

    # ---- CAPITAL ----
    capital_weather = get_weather_by_city(country["capital"])

    capital_scores = calculate_scores(
        capital_weather["temperature"],
        air["pm25"],  # simplificare
        country["population"]
    )

    capital_data = {
        "name": country["capital"],
        "temperature": capital_weather["temperature"],
        "description": capital_weather["description"],
        "pm25": air["pm25"],
        "population": country["population"],
        "currency": country["currency"],
        "image": get_city_image(country["capital"]),
        "scores": capital_scores
    }

    return {
        "city": city_data,
        "capital": capital_data
    }


# -----------------------
# COMPARISON
# -----------------------

def compare_bundles(bundle1, bundle2):

    city_winner = (
        bundle1["city"]["name"]
        if bundle1["city"]["scores"]["total"] >
           bundle2["city"]["scores"]["total"]
        else bundle2["city"]["name"]
    )

    capital_winner = (
        bundle1["capital"]["name"]
        if bundle1["capital"]["scores"]["total"] >
           bundle2["capital"]["scores"]["total"]
        else bundle2["capital"]["name"]
    )

    return {
        "city_winner": city_winner,
        "capital_winner": capital_winner
    }