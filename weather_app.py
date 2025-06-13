import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import requests
import geocoder
import speech_recognition as sr

API_KEY = "3c49fed72702a6132bb4d36fc2bd581e"  # <-- Replace with your OpenWeatherMap API key


def get_location():
    g = geocoder.ip('me')
    return g.city


def get_weather(city):
    try:
        weather_url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
        weather_data = requests.get(weather_url).json()

        if weather_data.get("cod") != 200:
            return None

        temp = weather_data['main']['temp']
        desc = weather_data['weather'][0]['main']
        icon = weather_data['weather'][0]['icon']
        lat = weather_data['coord']['lat']
        lon = weather_data['coord']['lon']

        aqi_url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={API_KEY}"
        aqi_data = requests.get(aqi_url).json()
        aqi = aqi_data['list'][0]['main']['aqi']

        return {
            "temp": temp,
            "desc": desc,
            "icon": icon,
            "aqi": aqi,
            "city": city.title()
        }

    except:
        return None


def aqi_description(aqi):
    descriptions = {
        1: "Good",
        2: "Fair",
        3: "Moderate",
        4: "Poor",
        5: "Very Poor"
    }
    return descriptions.get(aqi, "Unknown")


def get_background(desc):
    if "Rain" in desc:
        return "assets/rainy.jpg"
    elif "Cloud" in desc:
        return "assets/cloudy.jpg"
    elif "Clear" in desc:
        return "assets/sunny.jpg"
    else:
        return "assets/default.webp"


def update_ui(data):
    if not data:
        messagebox.showerror("Error", "Couldn't fetch weather data.")
        return

    bg_path = get_background(data["desc"])
    bg_image = Image.open(bg_path).resize((screen_width, screen_height))
    bg_photo = ImageTk.PhotoImage(bg_image)

    bg_label.configure(image=bg_photo)
    bg_label.image = bg_photo

    weather_label.config(
        text=f"{data['city']}\n{data['desc']}\n🌡️ {data['temp']} °C\nAQI: {data['aqi']} ({aqi_description(data['aqi'])})")
    weather_label.place(relx=0.5, rely=0.3, anchor="n")


def search_weather():
    city = entry.get()
    if city:
        data = get_weather(city)
        update_ui(data)


def voice_search():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        try:
            speak_label.config(text="Listening...")
            audio = recognizer.listen(source, timeout=5)
            text = recognizer.recognize_google(audio)
            speak_label.config(text=f"You said: {text}")
            entry.delete(0, tk.END)
            entry.insert(0, text)
            search_weather()
        except Exception:
            speak_label.config(text="Sorry, couldn't understand.")


# === GUI Setup ===
root = tk.Tk()
root.title("Python Weather App")

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

root.state('zoomed')  # Maximize window (not fullscreen)

# Optional: press ESC to quit the app
root.bind("<Escape>", lambda e: root.destroy())

bg_label = tk.Label(root)
bg_label.place(relwidth=1, relheight=1)

frame = tk.Frame(root, bg="#ffffff", bd=5)
frame.place(relx=0.5, rely=0.05, relwidth=0.9, relheight=0.1, anchor="n")

entry = tk.Entry(frame, font=("Arial", 18))
entry.place(relwidth=0.65, relheight=1)

search_btn = tk.Button(frame, text="Search", font=("Arial", 16), command=search_weather)
search_btn.place(relx=0.65, relwidth=0.2, relheight=1)

voice_btn = tk.Button(frame, text="🎤", font=("Arial", 16), command=voice_search)
voice_btn.place(relx=0.85, relwidth=0.15, relheight=1)

weather_label = tk.Label(root, font=("Arial", 40), bg="#ffffff", justify="center")
weather_label.place(relx=0.5, rely=0.3, anchor="n")

speak_label = tk.Label(root, text="", font=("Arial", 14), bg="#ffffff")
speak_label.place(relx=0.5, rely=0.85, anchor="n")

# Initial load weather for user location
user_city = get_location()
data = get_weather(user_city)
update_ui(data)

root.mainloop()
