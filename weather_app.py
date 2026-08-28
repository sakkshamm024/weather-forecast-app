import requests
import os
from dotenv import load_dotenv

# Load API key from .env
load_dotenv()

API_KEY = os.getenv("OPENWEATHER_API_KEY")


def get_current_weather(city):
    url = "https://api.openweathermap.org/data/2.5/weather"

    params = {
        "q": city,
        "appid": API_KEY,
        "units": "metric"
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()

        print("\n========================================")
        print("           CURRENT WEATHER")
        print("========================================")

        print(f"City        : {data['name']}")
        print(f"Temperature : {data['main']['temp']:.1f}°C")
        print(f"Feels Like  : {data['main']['feels_like']:.1f}°C")
        print(f"Condition   : {data['weather'][0]['description'].title()}")
        print(f"Humidity    : {data['main']['humidity']}%")
        print(f"Wind Speed  : {data['wind']['speed']:.1f} m/s")

        print("========================================")

        return True

    else:
        print("\nUnable to fetch current weather.")
        print("Status Code:", response.status_code)
        print("Error:", response.text)

        return False


def get_forecast(city):
    url = "https://api.openweathermap.org/data/2.5/forecast"

    params = {
        "q": city,
        "appid": API_KEY,
        "units": "metric"
    }

    response = requests.get(url, params=params)

    if response.status_code != 200:
        print("\nUnable to fetch weather forecast.")
        print("Status Code:", response.status_code)
        print("Error:", response.text)
        return

    data = response.json()

    # Store weather information by date
    daily_data = {}

    for forecast in data["list"]:

        date = forecast["dt_txt"].split(" ")[0]

        temperature = forecast["main"]["temp"]
        humidity = forecast["main"]["humidity"]
        condition = forecast["weather"][0]["description"]

        if date not in daily_data:
            daily_data[date] = {
                "temperatures": [],
                "humidity": [],
                "conditions": []
            }

        daily_data[date]["temperatures"].append(temperature)
        daily_data[date]["humidity"].append(humidity)
        daily_data[date]["conditions"].append(condition)

    print("\n========================================")
    print("          5-DAY WEATHER FORECAST")
    print("========================================")

    print(f"City: {data['city']['name']}")

    print("----------------------------------------")
    print("Date         Min     Max     Avg     Condition")
    print("----------------------------------------")

    for date, weather in list(daily_data.items())[:5]:

        temperatures = weather["temperatures"]
        humidity_values = weather["humidity"]
        conditions = weather["conditions"]

        min_temp = min(temperatures)
        max_temp = max(temperatures)
        avg_temp = sum(temperatures) / len(temperatures)

        # Most common weather condition
        condition = max(set(conditions), key=conditions.count)

        print(
            f"{date}   "
            f"{min_temp:5.1f}°C  "
            f"{max_temp:5.1f}°C  "
            f"{avg_temp:5.1f}°C  "
            f"{condition.title()}"
        )

    print("----------------------------------------")
    print("Forecast retrieved successfully.")
    print("========================================")


def main():

    print("\n========================================")
    print("       WEATHER DATA & FORECAST APP")
    print("========================================")

    while True:

        city = input(
            "\nEnter city name (or type 'exit' to quit): "
        ).strip()

        if city.lower() == "exit":
            print("\nThank you for using the Weather App!")
            break

        if not city:
            print("City name cannot be empty.")
            continue

        success = get_current_weather(city)

        if success:
            get_forecast(city)


if __name__ == "__main__":
    main()