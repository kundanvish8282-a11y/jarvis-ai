from AppOpener import close, open as appopen
from Backend.TextToSpeech import TextToSpeech
import subprocess
import pyautogui
import threading
import time
import webbrowser
import asyncio

# ------------------ FAST TTS ------------------
def speak(text):
    threading.Thread(target=TextToSpeech, args=(text,), daemon=True).start()

# ------------------ WHATSAPP STATE ------------------
WHATSAPP_MODE = {
    "active": False,
    "contact": None,
    "awaiting_choice": False,
    "last_search": ""
}

# ------------------ PATH ------------------
WHATSAPP_PATH = r"C:\Users\Kishan\AppData\Local\WhatsApp\WhatsApp.exe"

# ------------------ OPEN ------------------
def OpenWhatsApp():
    speak("Opening WhatsApp")

    try:
        subprocess.Popen(WHATSAPP_PATH)
    except:
        appopen("whatsapp", match_closest=True)

    time.sleep(5)

    WHATSAPP_MODE["active"] = True
    WHATSAPP_MODE["contact"] = None
    WHATSAPP_MODE["awaiting_choice"] = False


# ------------------ SEARCH CONTACT ------------------
def SearchContact(name):
    speak(f"Searching {name}")

    WHATSAPP_MODE["last_search"] = name

    pyautogui.hotkey("ctrl", "n")   # new chat
    time.sleep(1)

    pyautogui.write(name)
    time.sleep(2)

    speak(f"I found multiple {name}. Say first or second")
    WHATSAPP_MODE["awaiting_choice"] = True


# ------------------ SELECT CONTACT ------------------
def SelectChoice(choice):
    speak("Opening contact")

    if "first" in choice or "1" in choice:
        pyautogui.press("enter")

    elif "second" in choice or "2" in choice:
        pyautogui.press("down")
        time.sleep(0.5)
        pyautogui.press("enter")

    WHATSAPP_MODE["awaiting_choice"] = False
    WHATSAPP_MODE["contact"] = WHATSAPP_MODE["last_search"]


# ------------------ TYPE MESSAGE ------------------
def TypeMessage(text):
    pyautogui.write(text)


# ------------------ SEND ------------------
def SendMessage():
    speak("Sending message")
    pyautogui.press("enter")

    WHATSAPP_MODE["active"] = False
    WHATSAPP_MODE["contact"] = None


# ------------------ CLOSE ------------------
def CloseApp(app):
    app = app.lower()

    if "whatsapp" in app:
        speak("Closing WhatsApp")
        pyautogui.hotkey("alt", "f4")
        return True

    if "youtube" in app:
        speak("Closing YouTube")
        pyautogui.hotkey("ctrl", "w")
        return True

    try:
        close(app, match_closest=True)
        return True
    except:
        speak(f"{app} not running")
        return False


# ------------------ NORMAL OPEN ------------------
def SmartOpen(app):
    app = app.lower().strip()

    if app == "youtube":
        speak("Opening YouTube")
        webbrowser.open("https://www.youtube.com")
        return True

    try:
        speak(f"Opening {app}")
        appopen(app, match_closest=True)
        return True
    except:
        webbrowser.open(f"https://www.google.com/search?q={app}")
        return True


# ------------------ EXECUTION ------------------
async def ExecuteCommands(commands):

    for raw in commands:
        if not raw:
            continue

        cmd = raw.lower().strip()

        # ================= WHATSAPP MODE =================

        if WHATSAPP_MODE["active"]:

            # 🔥 WAITING FOR CHOICE
            if WHATSAPP_MODE["awaiting_choice"]:
                SelectChoice(cmd)
                continue

            # 🔥 SEND
            if cmd == "send":
                SendMessage()
                continue

            # 🔥 CONTACT SELECT
            if cmd.startswith("message "):
                name = cmd.replace("message", "").strip()
                SearchContact(name)
                continue

            # 🔥 TYPE MESSAGE
            TypeMessage(cmd)
            continue

        # ================= NORMAL =================

        if cmd.startswith("open whatsapp"):
            OpenWhatsApp()

        elif cmd.startswith("open "):
            SmartOpen(cmd[5:])

        elif cmd.startswith("close "):
            CloseApp(cmd[6:])

        elif cmd.startswith("play "):
            speak(f"Playing {cmd[5:]}")
            webbrowser.open(f"https://www.youtube.com/results?search_query={cmd[5:]}")

    return True


# ------------------ ENTRY ------------------
async def Automation(commands):
    return await ExecuteCommands(commands)