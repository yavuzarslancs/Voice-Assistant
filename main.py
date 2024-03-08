from playsound import playsound
import speech_recognition as sr
from gtts import gTTS
import os
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import threading
import time

class VoiceAssistant():
    def __init__(self):
        self.driver = None
        self.commands = {
            "selam": self.respond_hello,
            "video aç": self.ask_what_to_open,
            "müzik aç": self.ask_what_to_open,
            "şarkı aç": self.ask_what_to_open,
            "görüşürüz": self.close_application,
            "kapat": self.close_application,
            "çıkış": self.close_application,
            "dur": self.close_application
        }
        self.dubbing("Hoşgeldin, sana nasıl yardımcı olabilirim?")

    def dubbing(self, text):
        tts = gTTS(text, lang="tr")
        file_name = "file" + str(random.randint(1, 1000000000)) + ".mp3"
        tts.save(file_name)
        playsound(file_name)
        os.remove(file_name)

    def voice_record(self):
        r = sr.Recognizer()
        with sr.Microphone() as source:
            print("Dinleniyor...")
            audio = r.listen(source)
            voice_data = ""
            try:
                voice_data = r.recognize_google(audio, language="tr")
                print(voice_data)
            except sr.UnknownValueError:
                print("Ses anlaşılamadı")
            except sr.RequestError:
                print("Sistem çalışmıyor")
            return voice_data

    def open_browser(self, search_query):
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        self.driver.get(f"https://www.youtube.com/results?search_query={search_query}")
        try:
            video_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="video-title"]/yt-formatted-string'))
            )
            video_button.click()
            time.sleep(5)  # Bu süre video ve reklam durumuna göre değişebilir
        except Exception as e:
            print(f"Bir hata oluştu: {e}")
            self.close_browser()

    def voice_feedback(self, feedback_voice):
        for command, action in self.commands.items():
            if command in feedback_voice:
                action(feedback_voice)
                return  # Komut bulunduktan sonra döngüyü sonlandır

    def respond_hello(self, _):
        self.dubbing("Selamlar")

    def ask_what_to_open(self, _):
        self.dubbing("Ne açmamı istersin?")
        data = self.voice_record()
        if data:  # Kullanıcıdan sesli yanıt alındıysa
            browser_thread = threading.Thread(target=self.open_browser, args=(data,))
            browser_thread.start()

    def close_application(self, _):
        self.dubbing("Görüşmek üzere")
        if self.driver:
            self.driver.quit()
            self.driver = None  # Tarayıcı kapatıldıktan sonra driver'ı sıfırla

    def close_browser(self):
        if self.driver:
            self.driver.quit()
            self.driver = None  # Tarayıcı kapatıldıktan sonra driver'ı sıfırla

if __name__ == "__main__":
    assistant = VoiceAssistant()
    try:
        while True:
            voice_input = assistant.voice_record()
            if voice_input:
                voice_input = voice_input.lower()
                assistant.voice_feedback(voice_input)
    except KeyboardInterrupt:
        print("Program sonlandırıldı")
    finally:
        assistant.close_browser()
