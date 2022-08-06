import os

class Settings:
    TELEGRAM_BOT_TOKEN = os.environ.get("TG_BOT_TOKEN", "") # Telegram Bot Token
    WEATHER_API_KEY = os.environ.get("OW_TOKEN", "") # OpenWeatherMap API Key
    WEATHER_EXCLUDE = 'minutely,hourly,alerts' # OpenWeatherMap Exclude
    WEATHER_UNITS = 'metric' # OpenWeatherMap Units
    WEATHER_LANG = 'ru' # OpenWeatherMap Language
