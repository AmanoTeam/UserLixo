import re
from hydrogram import Client, filters
from hydrogram.types import Message

from utils import http 
from locales import use_lang

# Configurações da API Weather.com (IBM)
WEATHER_APIKEY = "8de2d8b3a93542c9a2d8b3a935a2c909"
GEO_URL = "https://api.weather.com/v3/location/search"
WEATHER_URL = "https://api.weather.com/v3/aggcommon/v3-wx-observations-current"

HEADERS = {
    "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 12; M2012K11AG Build/SQ1D.211205.017)"
}

STATUS_EMOJIS = {
    0: "⛈", 1: "⛈", 2: "⛈", 3: "⛈", 4: "⛈", 5: "🌨", 6: "🌨", 7: "🌨", 
    8: "🌨", 9: "🌨", 10: "🌨", 11: "🌧", 12: "🌧", 13: "🌨", 14: "🌨", 
    15: "🌨", 16: "🌨", 17: "⛈", 18: "🌧", 19: "🌫", 20: "🌫", 21: "🌫", 
    22: "🌫", 23: "🌬", 24: "🌬", 25: "🌨", 26: "☁️", 27: "🌥", 28: "🌥", 
    29: "⛅️", 30: "⛅️", 31: "🌙", 32: "☀️", 33: "🌤", 34: "🌤", 35: "⛈", 
    36: "🔥", 37: "🌩", 38: "🌩", 39: "🌧", 40: "🌧", 41: "❄️", 42: "❄️", 
    43: "❄️", 44: "n/a", 45: "🌧", 46: "🌨", 47: "🌩",
}

def get_emoji(code):
    return STATUS_EMOJIS.get(code, "🌡")

@Client.on_message(filters.command(["clima", "weather"], prefixes=".") & filters.sudoers)
@use_lang()
async def weather_cmd(c: Client, m: Message, t):
    # Verifica se o usuário passou a cidade
    if len(m.command) < 2:
        return await m.edit(t("weather_usage"))

    location_query = " ".join(m.command[1:])
    await m.edit(t("weather_search").format(location_query=location_query))

    try:
        # 1. Busca as Coordenadas (Geocoding)
        geo_params = {
            "apiKey": WEATHER_APIKEY,
            "format": "json",
            "language": t("weather_language"),
            "query": location_query,
        }
        
        r_geo = await http.get(GEO_URL, params=geo_params, headers=HEADERS, timeout=10)
        loc_data = r_geo.json()

        if not loc_data.get("location") or not loc_data["location"].get("latitude"):
            return await m.edit(t("location_not_found").format(location=location_query))

        # Pega o primeiro resultado da busca
        lat = loc_data["location"]["latitude"][0]
        lon = loc_data["location"]["longitude"][0]
        full_name = loc_data["location"]["address"][0]

        # 2. Busca o Clima Atual usando as Coordenadas
        weather_params = {
            "apiKey": WEATHER_APIKEY,
            "format": "json",
            "language": t("weather_language"),
            "geocode": f"{lat},{lon}",
            "units": t("measurement_unit"),
        }

        r_weather = await http.get(WEATHER_URL, params=weather_params, headers=HEADERS, timeout=10)
        res_json = r_weather.json()

        obs = res_json.get("v3-wx-observations-current")
        if not obs:
            return await m.edit(t("weather_err_data"))

        # 3. Formata a Resposta Final
        emoji = get_emoji(obs.get("iconCode"))
        phrase = obs.get("wxPhraseLong", "Desconhecido")
        
        text = t("details").format(
            location=full_name,
            temperature=obs.get("temperature"),
            feels_like=obs.get("temperatureFeelsLike"),
            air_humidity=obs.get("relativeHumidity"),
            wind_speed=obs.get("windSpeed"),
            overview=f"{emoji} {phrase}"
        )

        await m.edit(text)

    except Exception as e:
        # Log de erro básico para não travar o userbot
        await m.edit(t("ip_err_search")) 
