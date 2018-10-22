import requests
from weatherfood import application

app = application.app
API_KEY = app.config['API_KEY']
BASE_URL = "http://api.openweathermap.org/data/2.5/weather?zip={0},us&appid={1}"
RESULT_BASE = "{0}, and {1} degrees Fahrenheit"

def _kelvin_to_fahrenheit(k):
    f = (k * 1.8) - 459.67
    return int(f)

def get_weather_pretty(zipcode):
    raw = requests.post(BASE_URL.format(zipcode, API_KEY)).json()
    try:
        conditions = raw["weather"][0]["main"]
        temperature = _kelvin_to_fahrenheit(raw["main"]["temp"])
    except KeyError:
        return "Unavailable"
    else:
        return RESULT_BASE.format(conditions, temperature)
