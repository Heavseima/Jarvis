import requests
import wikipedia
import pywhatkit as kit
from email.message import EmailMessage
import smtplib
import gtts
import os
from pydub import AudioSegment
from pydub.playback import play
from decouple import config
from constant import (
    EMAIL,
    PASSWORD,
    IP_ADDR_API_URL,
    NEWS_FETCH_API_URL,
    NEWS_FETCH_API_KEY,
    WEATHER_FORECAST_API_KEY,
    WEATHER_FORECAST_API_URL,
    STMP_PORT,
    STMP_URL
)

def speak(text):
    try:
        # Use gTTS with clear pronunciation
        tts = gtts.gTTS(text, lang="en")
        tts.save("output.wav")
        
        # Load and process audio
        audio = AudioSegment.from_file("output.wav")
        os.remove("output.wav")
        
        # Basic audio enhancement
        audio = audio + 3  # Slight volume boost
        audio = audio.speedup(playback_speed=1.2)
        
        # Play the audio
        play(audio)
    
    except Exception as e:
        print(f"TTS Error: {e}")
        print(text)
        
def find_my_ip():
    ip_address = requests.get('https://api.ipify.org?format=json').json()
    return ip_address["ip"]

def search_on_wikipedia(query):
    results = wikipedia.summary(query, sentences=2)
    return results

def search_on_google(query):
    kit.search(query)
    
def youtube(video):
    kit.playonyt(video)
    
def send_email(reciever_add, subject, message):
    try:
        email = EmailMessage()
        email["To"] = reciever_add
        email["Subject"] = subject
        email["from"] = EMAIL
        
        email.set_content(message)
        s = smtplib.SMTP("smtp.gmail.com", 587)
        s.starttls()
        s.login(EMAIL, PASSWORD)
        s.send_message(email)
        s.close()
        return True
    
    except Exception as e:
        print(e)
        return False
    
def get_news():
    try:
        news_headline = []
        result = requests.get(
            NEWS_FETCH_API_URL,
            params={
                "country":"in",
                "category":"general",
                "apiKey": NEWS_FETCH_API_KEY
            },
        ).json()
        articles = result["articles"]
        for article in articles:
            news_headline.append(article["title"])
        
        # Convert list to a single string, joining headlines
        if news_headline:
            return ". ".join(news_headline[:6]) + "."
        else:
            return "Sorry, no news headlines are available right now."
    except Exception as e:
        print(f"Error fetching news: {e}")
        return "Sorry, I couldn't fetch the news headlines at the moment."


def weather_forecast(city):
    res = requests.get(
        WEATHER_FORECAST_API_URL,
        params={
            "q":city,
            "appid":WEATHER_FORECAST_API_KEY,
            "units":"metric"
        },
        ).json()
    weather = res["weather"][0]["main"]
    temp = res["main"]["temp"]
    feels_like = res["main"]["feels_like"]
    return weather, f"{temp}°C", f"{feels_like}°C"

    