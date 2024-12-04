import threading
import keyboard
import numpy as np
import sounddevice as sd
import speech_recognition as sr
import os
import time
import pyautogui
import subprocess as sp
import webbrowser
import imdb
from kivy.uix import widget, image, label, boxlayout, textinput
from kivy import clock
from constant import SCREEN_HEIGHT, SCREEN_WIDTH, GEMINI_API_KEY
from utils import speak, youtube, search_on_google, search_on_wikipedia, send_email, get_news, weather_forecast, find_my_ip
from jarvis_button import JarvisButton
import google.generativeai as genai

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

class Jarvis(widget.Widget):
    def __init__(self, **kwargs):
        super(Jarvis, self).__init__(**kwargs)
        self.volume = 0
        self.volume_history = [0, 0, 0, 0, 0, 0, 0]
        self.volume_history_size = 140
        
        self.min_size = .2 * SCREEN_WIDTH
        self.max_size = .7 * SCREEN_WIDTH
        
        self.add_widget(image.Image(source='static/border.eps.png', size=(1920, 1080)))
        self.circle = JarvisButton(size=(284.0, 284.0), background_normal='static/circle.png')
        self.circle.bind(on_press=self.start_recording)
        self.start_recording()
        self.add_widget(image.Image(source='static/jarvis.gif', size=(self.min_size, self.min_size), pos=(SCREEN_WIDTH / 2 - self.min_size / 2, SCREEN_HEIGHT / 2 - self.min_size / 2)))
        
        time_layout = boxlayout.BoxLayout(orientation='vertical', pos=(150, 900))
        self.time_label = label.Label(text='', font_size=24, markup=True, font_name='static/mw.ttf')
        time_layout.add_widget(self.time_label)
        self.add_widget(time_layout)
        
        self.title = label.Label(text='[b][color=3333ff][/color][/b]', font_size=42, markup=True, font_name='static/dusri.ttf', pos=(920, 900))
        self.add_widget(self.title)
        
        self.subtitles_input = textinput.TextInput(
            text='Hey Franklin! I am your personal assistant',
            font_size=24,
            readonly=False,
            background_color=(0, 0, 0, 0),
            foreground_color=(1, 1, 1, 1),
            size_hint_y=None,
            height=80,
            pos=(720, 100),
            width=1200,
            font_name='static/teesri.otf',
        )
        self.add_widget(self.subtitles_input)
        
        self.vrh = label.Label(text='', font_size=30, markup=True, font_name='static/mw.ttf', pos=(1500, 500))
        self.add_widget(self.vrh)
        
        self.vlh = label.Label(text='', font_size=30, markup=True, font_name='static/mw.ttf', pos=(400, 500))
        self.add_widget(self.vlh)
        self.add_widget(self.circle)
        keyboard.add_hotkey('`', self.start_recording)
        
    def take_command(self):
        r = sr.Recognizer()
        with sr.Microphone() as source:
            print("Listening...")
            r.pause_threshold = 1.5  
            r.adjust_for_ambient_noise(source, duration=1)  
            try:
                audio = r.listen(source, timeout=5) 
            except sr.WaitTimeoutError:
                speak("Sorry, I didn't hear anything. Please try again.")
                return 'None'

        try:
            print("Recognizing...")
            query = r.recognize_google(audio, language='en-in')
            return query.lower()
        except sr.UnknownValueError:
            speak("Sorry, I couldn't understand. Can you please repeat that?")
            return 'None'
        except sr.RequestError as e:
            speak("Sorry, there was an issue with the speech recognition service.")
            print(f"Request error: {e}")
            return 'None'
            
    def start_recording(self, *args):
        if not hasattr(self, "recording_thread") or not self.recording_thread.is_alive():
            self.recording_thread = threading.Thread(target=self.run_speech_recognition)
            self.recording_thread.start() 
            
    def run_speech_recognition(self):
        print('Initializing speech recognition...')
        r = sr.Recognizer()
        with sr.Microphone(sample_rate=16000) as source:
            r.adjust_for_ambient_noise(source, duration=1)  
            print("Listening...")
            
            audio = r.listen(source, 
                            phrase_time_limit=None,  
                            timeout=None,           
                            snowboy_configuration=None)
            
            print("Audio recorded")
        
        try:
            query = r.recognize_google(audio, language="en-in")
            print(f'Recognized: {query}')
            clock.Clock.schedule_once(lambda dt: setattr(self.subtitles_input, 'text', query))
            self.handle_jarvis_commands(query.lower())
        except sr.UnknownValueError:
            print("Could not understand audio")
        except sr.RequestError as e:
            print(f"Could not request results; {e}")
            
    def update_time(self, dt):
        current_time = time.strftime('TIME\n\t%H:%M:%S')
        self.time_label.text = f'[b][color=3333ff]{current_time}[/color][/b]'
        
    def update_circle(self, dt):
        try:
            self.size_value = int(np.mean(self.volume_history))
        except Exception as e:
            self.size_value = self.min_size
            print('Warning:', e)
            
        if self.size_value <= self.min_size:
            self.size_value = self.min_size
        elif self.size_value >= self.max_size:
            self.size_value = self.max_size                                     
        self.circle.size = (self.size_value, self.size_value)
        self.circle.pos = (SCREEN_WIDTH / 2 - self.circle.width / 2, SCREEN_HEIGHT / 2 - self.circle.height / 2)
        
    def update_volume(self, indata, frames, time, status):
        volume_norm = np.linalg.norm(indata) * 200
        self.volume = volume_norm
        self.volume_history.append(volume_norm)
        self.vrh.text = f'[b][color=3333ff]{np.mean(self.volume_history)}[/color][/b]'
        self.vlh.text = f'[b][color=3333ff]{np.mean(self.volume_history)}[/color][/b]'
        self.vlh.text = f'''[b][color=3344ff]
            {round(self.volume_history[0], 7)}\n
            {round(self.volume_history[1], 7)}\n
            {round(self.volume_history[2], 7)}\n
            {round(self.volume_history[3], 7)}\n
            {round(self.volume_history[4], 7)}\n
            {round(self.volume_history[5], 7)}\n
            {round(self.volume_history[6], 7)}\n
            [/color][/b]'''
            
        self.vrh.text = f'''[b][color=3344ff]
            {round(self.volume_history[0], 7)}\n
            {round(self.volume_history[1], 7)}\n
            {round(self.volume_history[2], 7)}\n
            {round(self.volume_history[3], 7)}\n
            {round(self.volume_history[4], 7)}\n
            {round(self.volume_history[5], 7)}\n
            {round(self.volume_history[6], 7)}\n
            [/color][/b]'''  
            
        if len(self.volume_history) > self.volume_history_size:
            self.volume_history.pop(0)  
    
    def start_listening(self):
        self.stream = sd.InputStream(callback=self.update_volume) 
        self.stream.start()
    
    def get_gemini_response(self, query):
        try:
            response = model.generate_content(query)
            return response.text
        except Exception as e:
            print(f"Error getting Gemini response: {e}")
            return "I'm sorry, I couldn't process that request."
            
    def handle_jarvis_commands(self, query):  
        try:
            if "how are you" in query:
                speak("I am absolutely fine sir. What about you")
            elif "open command prompt" in query:
                speak("Opening command prompt")
                os.system('start cmd')
            elif "open camera" in query:
                speak("Opening camera sir")
                sp.run('start microsoft.windows.camera:', shell=True)
            elif "open notepad" in query:
                speak("Opening Notepad for you sir")
                notepad_path = "C:\\Windows\\notepad.exe"
                os.startfile(notepad_path)
            elif "open discord" in query:
                speak("Opening Discord for you sir")
                discord_path = "C:\\Users\\U-ser\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Discord Inc\\Discord.lnk"
                os.startfile(discord_path)
            elif "open mlbb" in query or "open mobile legend bang bang" in query or "open mobile legend" in query or "open ml" in query:
                speak("Opening Mobile Legend Bang Bang for you sir")
                mlbb_path = "C:\\Users\\U-ser\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Google Play Games\\Mobile Legends Bang Bang.lnk"
                os.startfile(mlbb_path)
            elif 'ip address' in query:
                ip_address = find_my_ip()
                speak(f'Your IP Address is {ip_address}.\n For your convenience, I am printing it on the screen sir.')
                print(f'Your IP Address is {ip_address}')
            elif "youtube" in query:
                speak("What do you want to play on youtube sir?")
                video = self.take_command().lower()
                speak(f"Opening {video} for you sir!")
                youtube(video)
            elif "google" in query:
                speak("What do you want to search on google")
                query = self.take_command().lower()
                speak(f"search {query} on google for you now sir")
                search_on_google(query)
            elif "wikipedia" in query:
                speak("What do you want to search on wikipedia sir?")
                search = self.take_command().lower()
                results = search_on_wikipedia(search)
                speak(f"According to Wikipedia, {results}")
            elif "email" in query:
                speak("On what email address do you want to send sir? Please enter in the terminal")
                receiver_add = input("Email address:")
                speak("What should be the subject sir?")
                subject = self.take_command().capitalize()
                speak("What is the message?")
                message = self.take_command().capitalize()
                if send_email(receiver_add, subject, message):
                    speak("I have sent the email sir")
                    print("I have sent the email sir")
                else:
                    speak("Something went wrong. Please check the error log")
            elif "news" in query:
                speak("I am reading out the latest headline of today, sir")
                speak(get_news())
            elif 'weather' in query:
                ip_address = find_my_ip()
                speak("Tell me the name of your city")
                city = self.take_command().lower()
                speak(f"Getting weather report for your city {city}")
                weather, temp, feels_like = weather_forecast(city)
                speak(f"The current temperature is {temp}, but it feels like {feels_like}")
                speak(f"Also, the weather report talks about {weather}")
                print(f"Description: {weather}\nTemperature: {temp}\nFeels like: {feels_like}")
            elif "movie" in query:
                movies_db = imdb.IMDb()
                speak("Please tell me the movie name:")
                text = self.take_command().lower()
                movies = movies_db.search_movie(text)
                speak("Searching for " + text)
                speak("I found these:")
                for movie in movies:
                    try:
                        title = movie.get("title", "Unknown Title")
                        year = movie.get("year", "Unknown Year")
                        movie_message = f"{title} - {year}"
                        speak(movie_message)

                        info = movie.getID()
                        movie_info = movies_db.get_movie(info)

                        rating = movie_info.get("rating", "No rating available")

                        cast = movie_info.get("cast", [])
                        actor_names = []
                        for person in cast[:5]:  
                            try:
                                actor_names.append(str(person))
                            except Exception:
                                continue

                        plot = movie_info.get("plot", ["No plot available"])[0]

                        if actor_names:
                            cast_message = f"Rating: {rating}, Cast: {', '.join(actor_names)}"
                        else:
                            cast_message = f"Rating: {rating}"
                        
                        speak(cast_message)
                        print(f"Plot: {plot}")

                    except Exception as e:
                        print(f"Error processing movie {movie}: {e}")
            
            else:
                gemini_response = self.get_gemini_response(query)
                gemini_response = gemini_response.replace("*","")
                if gemini_response and gemini_response != "I'm sorry, I couldn't process that request.":
                    speak(gemini_response)
                    print(gemini_response)
                    
        except Exception as e:
            print(f"Error handling commands: {e}")

