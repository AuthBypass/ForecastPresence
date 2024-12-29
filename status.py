import requests
import time
from datetime import datetime
from pytz import timezone
import os

discord_token = os.getenv("DISCORD_TOKEN")
weather_api_key = os.getenv("WEATHER_API_KEY")
latitude = float(os.getenv("LATITUDE"))
longitude = float(os.getenv("LONGITUDE"))

local_tz = timezone("Europe/Berlin")

def change_status(token, message):
    headers = {'authorization': token}
    json_data = {
        "custom_status": {"text": message}
    }
    requests.patch("https://discord.com/api/v10/users/@me/settings", headers=headers, json=json_data)

def get_current_time():
    current_time = datetime.now(local_tz)
    return current_time.strftime("%H:%M")

def get_weather_emoji(weather_description, current_time, sunrise_time, sunset_time):
    if "clear" in weather_description or "sunny" in weather_description:
        weather_emoji = "☀️" if sunrise_time <= current_time <= sunset_time else "🌙"
    elif "cloud" in weather_description:
        weather_emoji = "☁️"
    elif "rain" in weather_description or "drizzle" in weather_description:
        weather_emoji = "🌧️"
    elif "thunderstorm" in weather_description:
        weather_emoji = "⛈️"
    elif "snow" in weather_description:
        weather_emoji = "❄️"
    elif "mist" in weather_description or "fog" in weather_description:
        weather_emoji = "🌫️"
    else:
        weather_emoji = "🌈"

    return weather_emoji

def get_weather_and_sun_times():
    weather_url = f"https://api.weatherapi.com/v1/forecast.json?key={weather_api_key}&q={latitude},{longitude}&days=1"
    response = requests.get(weather_url)
    if response.status_code == 200:
        weather_data = response.json()
        try:
            weather_main = weather_data['current']['condition']['text'].lower()
            sunrise_time_str = weather_data['forecast']['forecastday'][0]['astro']['sunrise']
            sunset_time_str = weather_data['forecast']['forecastday'][0]['astro']['sunset']

            sunrise_time = datetime.strptime(sunrise_time_str, '%I:%M %p').time()
            sunset_time = datetime.strptime(sunset_time_str, '%I:%M %p').time()

            return weather_main, sunrise_time, sunset_time
        except KeyError as e:
            print(f"Key error: {e}")
        except ValueError as e:
            print(f"Value error: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")
    else:
        print(f"Weather API error: {response.status_code} - {response.text}")
    return "Clear", None, None

previous_status = None
last_weather_update = time.time()

while True:
    current_time = get_current_time()
    if time.time() - last_weather_update > 1800 or previous_status is None:
        weather_main, sunrise_time, sunset_time = get_weather_and_sun_times()
        last_weather_update = time.time()
    current_time_obj = datetime.strptime(current_time, "%H:%M").time()
    weather_emoji = get_weather_emoji(weather_main, current_time_obj, sunrise_time, sunset_time)
    status_message = f"{weather_emoji} | {current_time}"
    if status_message != previous_status:
        change_status(discord_token, status_message)
        print(f"Status updated to: {status_message}")
        previous_status = status_message
    time.sleep(1)
