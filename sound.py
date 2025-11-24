# import pyttsx3
# def speak(text):
#     try:
#         engine = pyttsx3.init()   # create fresh engine each time
#         engine.setProperty('rate', 150)
#         engine.say(text)
#         engine.runAndWait()
#         engine.stop()
#     except Exception as e:
#         print("Speech error:", e)



import pyttsx3
import threading

def speak(text):
    def run_speech():
        try:
            engine = pyttsx3.init()   # create separate engine for each speech
            engine.setProperty('rate', 150)
            engine.say(text)
            engine.runAndWait()
            engine.stop()
        except Exception as e:
            print("Speech error:", e)

    threading.Thread(target=run_speech, daemon=True).start()
