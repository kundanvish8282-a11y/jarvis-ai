# ================= LUCKY MAIN =================

import threading
import subprocess
import time
from time import sleep
import asyncio
from dotenv import dotenv_values
import pyautogui

# ================= GUI =================
from Frontend.GUI import (
    GraphicalUserInterface,
    SetAssistantStatus,
    ShowTextToScreen,
    SetMicrophoneStatus,
    QueryModifier,
    GetMicrophoneStatus
)

# ================= BACKEND =================
from Backend.Model import FirstLayerDMM
from Backend.Automation import Automation
from Backend.SpeechToText import SpeechRecognition
from Backend.Chatbot import ChatBot
from Backend.TextToSpeech import TextToSpeech, StopSpeech

# ================= ENV =================
env = dotenv_values(".env")
Username = env.get("USERNAME", "User")
Assistantname = env.get("ASSISTANT_NAME", "Lucky")

# ================= CONSTANTS =================
STOP_WORDS = ["stop", "cancel", "pause", "quiet"]

EXECUTION_LOCK = threading.Lock()
STOP_ALL = False

# ================= FAST TTS =================
def speak(text):
    threading.Thread(target=TextToSpeech, args=(text,), daemon=True).start()

# ================= SAFE ASYNC =================
def safe_run(coro):
    try:
        asyncio.run(coro)
    except:
        pass

# ================= INIT =================
def InitialExecution():
    SetMicrophoneStatus("False")
    ShowTextToScreen("")

InitialExecution()

# ================= MAIN =================
def MainExecution():
    global STOP_ALL

    if not EXECUTION_LOCK.acquire(blocking=False):
        return

    try:
        query = SpeechRecognition()

        if not query:
            return

        query = query.strip()

        # 🔥 ALWAYS SHOW USER SPEECH
        ShowTextToScreen(f"{Username} : {query}")

        q = query.lower()

        # ===== GREETING (🔥 NEW) =====
        if q in ["hello", "hi", "hey", "hlo"]:
            response = f"Hello {Username}, I am {Assistantname}. What can I help you?"
            ShowTextToScreen(f"{Assistantname} : {response}")
            speak(response)
            return

        # ===== STOP =====
        if any(w in q for w in STOP_WORDS):
            STOP_ALL = True
            StopSpeech()
            speak("Stopped")
            return

        SetAssistantStatus("Processing...")

        decision = FirstLayerDMM(q)
        print("Decision:", decision)

        if not decision:
            return

        # =====================================================
        # 🔥 SHOW COMMAND
        # =====================================================
        ShowTextToScreen(f"{Assistantname} (Command) : {', '.join(decision)}")

        # =====================================================
        # 🔥 SPEAK ACTION
        # =====================================================
        for cmd in decision:
            if cmd.startswith("open "):
                speak(f"Opening {cmd.replace('open ', '')}")

            elif cmd.startswith("close "):
                speak(f"Closing {cmd.replace('close ', '')}")

            elif cmd.startswith("play "):
                speak(f"Playing {cmd.replace('play ', '')}")

            elif cmd.startswith("google search "):
                speak("Searching Google")

            elif cmd.startswith("youtube search "):
                speak("Searching YouTube")

            elif cmd.startswith("message "):
                speak("Opening chat")

            elif cmd == "send":
                speak("Sending message")

        # =====================================================
        # 🔥 EXECUTE (IMPORTANT)
        # =====================================================
        safe_run(Automation(decision))

        # =====================================================
        # CHAT RESPONSE (ONLY WHEN NEEDED)
        # =====================================================
        merged = " ".join(
            cmd.replace("general", "").replace("realtime", "").strip()
            for cmd in decision
            if cmd.startswith(("general", "realtime"))
        )

        if merged:
            answer = ChatBot(QueryModifier(merged))
            ShowTextToScreen(f"{Assistantname} : {answer}")
            speak(answer)

    except Exception as e:
        print("Main Error:", e)

    finally:
        SetAssistantStatus("Available...")
        EXECUTION_LOCK.release()

# ================= THREADS =================
def VoiceThread():
    active = False

    while True:
        mic = GetMicrophoneStatus()

        if mic == "True" and not active:
            active = True
            SetAssistantStatus("Listening...")

        if mic == "True":
            MainExecution()
        else:
            active = False

        sleep(0.05)

def GUIThread():
    GraphicalUserInterface()

# ================= RUN =================
if __name__ == "__main__":
    threading.Thread(target=VoiceThread, daemon=True).start()
    GUIThread()