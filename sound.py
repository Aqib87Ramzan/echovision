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
# import pyttsx3
# import threading
# import queue
# import time

# # Queue to store all speech messages
# speech_queue = queue.Queue()

# # Initialize pyttsx3 engine once
# engine = pyttsx3.init()
# engine.setProperty('rate', 150)

# # Lock to prevent overlapping runAndWait calls
# engine_lock = threading.Lock()

# def speech_worker():
#     while True:
#         text = speech_queue.get()
#         if text is None:
#             break  # allows clean exit
#         try:
#             with engine_lock:  # ensure only one runAndWait at a time
#                 engine.say(text)
#                 engine.runAndWait()
#         except Exception as e:
#             print("Speech error:", e)
#         finally:
#             speech_queue.task_done()
#         time.sleep(0.05)  # small pause to avoid queue pileup

# # Start the worker thread
# threading.Thread(target=speech_worker, daemon=True).start()

# def speak(text):
#     """
#     Add text to the queue to be spoken in order.
#     """
#     speech_queue.put(text)
