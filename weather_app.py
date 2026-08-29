import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

API_KEY = os.getenv("OPENWEATHER_API_KEY")

BASE_URL = "https://api.openweathermap.org/data/2.5"


def get_current_weather(city):
    url = f"{BASE_URL}/weather"

    params = {
        "q": city,
        "appid": API_KEY,
        "units": "metric"
    }

    try:
        response = requests.get(url, params=params, timeout=10)

        if response.status_code == 404:
            print("\nCity not found. Please check the city name.")
            return False

        if response.status_code == 401:
            print("\nInvalid API key.")
            return False

        if response.status_code != 200:
            print("\nUnable to fetch weather information.")
            print("Status Code:", response.status_code)
            return False

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

    except requests.exceptions.Timeout:
        print("\nRequest timed out. Please try again.")

    except requests.exceptions.ConnectionError:
        print("\nNetwork error. Please check your internet connection.")

    except requests.exceptions.RequestException as error:
        print("\nAn error occurred while connecting to the weather service.")
        print("Error:", error)

    return False


def get_forecast(city):
    url = f"{BASE_URL}/forecast"

    params = {
        "q": city,
        "appid": API_KEY,
        "units": "metric"
    }

    try:
        response = requests.get(url, params=params, timeout=10)

        if response.status_code != 200:
            print("\nUnable to fetch forecast.")
            return

        data = response.json()

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
            conditions = weather["conditions"]

            min_temp = min(temperatures)
            max_temp = max(temperatures)
            avg_temp = sum(temperatures) / len(temperatures)

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

    except requests.exceptions.Timeout:
        print("\nForecast request timed out.")

    except requests.exceptions.ConnectionError:
        print("\nNetwork error while fetching forecast.")

    except requests.exceptions.RequestException as error:
        print("\nAn error occurred.")
        print("Error:", error)


def main():

    print("\n========================================")
    print("       WEATHER DATA & FORECAST APP")
    print("========================================")

    if not API_KEY:
        print("\nAPI key not found!")
        print("Please check your .env file.")
        return

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