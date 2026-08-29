from flask import Flask, render_template, request
import requests
import os
from dotenv import load_dotenv
from datetime import datetime, timezone, timedelta

load_dotenv()

app = Flask(__name__)

API_KEY = os.getenv("OPENWEATHER_API_KEY")


def get_weather_data(city):
    current_url = "https://api.openweathermap.org/data/2.5/weather"
    forecast_url = "https://api.openweathermap.org/data/2.5/forecast"

    params = {
        "q": city,
        "appid": API_KEY,
        "units": "metric"
    }

    try:
        current_response = requests.get(
            current_url,
            params=params,
            timeout=10
        )

        if current_response.status_code != 200:
            return None, None, current_response.status_code

        current_data = current_response.json()

        timezone_offset = current_data.get("timezone", 0)

        local_time = datetime.now(
            timezone.utc
        ) + timedelta(seconds=timezone_offset)

        sunrise_time = datetime.fromtimestamp(
            current_data["sys"]["sunrise"],
            timezone.utc
        ) + timedelta(seconds=timezone_offset)

        sunset_time = datetime.fromtimestamp(
            current_data["sys"]["sunset"],
            timezone.utc
        ) + timedelta(seconds=timezone_offset)

        weather = {
            "city": current_data["name"],
            "country": current_data["sys"]["country"],
            "temperature": round(current_data["main"]["temp"], 1),
            "feels_like": round(current_data["main"]["feels_like"], 1),
            "condition": current_data["weather"][0]["description"].title(),
            "icon": current_data["weather"][0]["icon"],
            "humidity": current_data["main"]["humidity"],
            "wind_speed": round(current_data["wind"]["speed"], 1),
            "latitude": round(current_data["coord"]["lat"], 4),
            "longitude": round(current_data["coord"]["lon"], 4),
            "date": local_time.strftime("%A, %d %B %Y"),
            "time": local_time.strftime("%I:%M %p"),
            "sunrise": sunrise_time.strftime("%I:%M %p"),
            "sunset": sunset_time.strftime("%I:%M %p")
        }

        forecast_response = requests.get(
            forecast_url,
            params=params,
            timeout=10
        )

        if forecast_response.status_code != 200:
            return weather, None, 500

        forecast_data = forecast_response.json()

        daily_forecasts = {}

        for item in forecast_data["list"]:

            forecast_datetime = datetime.fromtimestamp(
                item["dt"],
                timezone.utc
            ) + timedelta(
                seconds=forecast_data["city"].get("timezone", 0)
            )

            date = forecast_datetime.strftime("%Y-%m-%d")
            temperature = item["main"]["temp"]

            if date not in daily_forecasts:

                daily_forecasts[date] = {
                    "day": forecast_datetime.strftime("%A"),
                    "date": forecast_datetime.strftime("%d %b"),
                    "high": temperature,
                    "low": temperature,
                    "condition": item["weather"][0]["description"].title(),
                    "icon": item["weather"][0]["icon"]
                }

            else:

                daily_forecasts[date]["high"] = max(
                    daily_forecasts[date]["high"],
                    temperature
                )

                daily_forecasts[date]["low"] = min(
                    daily_forecasts[date]["low"],
                    temperature
                )

        forecast = list(daily_forecasts.values())[:5]

        for day in forecast:
            day["high"] = round(day["high"])
            day["low"] = round(day["low"])

        return weather, forecast, 200

    except requests.exceptions.RequestException:
        return None, None, 503


@app.route("/", methods=["GET", "POST"])
def home():

    weather = None
    forecast = None
    error = None
    city = ""

    if request.method == "POST":

        city = request.form.get("city", "").strip()

        if not city:

            error = "Please enter a city name."

        else:

            weather, forecast, status = get_weather_data(city)

            if status == 404:
                error = "City not found. Please check the city name."

            elif status == 401:
                error = "Invalid API key."

            elif status == 503:
                error = "Network error. Please check your internet connection."

            elif status != 200:
                error = "Unable to fetch weather information."

    return render_template(
        "index.html",
        weather=weather,
        forecast=forecast,
        error=error,
        city=city
    )


if __name__ == "__main__":
    app.run(debug=True)