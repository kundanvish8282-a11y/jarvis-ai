from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import dotenv_values
import mtranslate as mt
import os
import time
from pathlib import Path

# ================== LOAD ENV ==================
env_vars = dotenv_values(".env")
InputLanguage = env_vars.get("INPUT_LANGUAGE", "hi").lower()   # 🔥 default Hindi
print(f"Input Language: {InputLanguage}")

# ================== PATH ==================
BASE_DIR = Path(__file__).resolve().parent
VOICE_HTML = BASE_DIR / "Data" / "Voice.html"
VOICE_HTML.parent.mkdir(exist_ok=True)

# ================== CREATE HTML ==================
HtmlCode = f"""
<!DOCTYPE html>
<html>
<head>
<title>LISTENING</title>
</head>
<body>
<script>
    var rec = new webkitSpeechRecognition();
    rec.lang = "{InputLanguage}";
    rec.continuous = false;
    rec.interimResults = false;

    rec.onresult = function(e) {{
        document.title = e.results[0][0].transcript;
    }};

    rec.onerror = function() {{
        document.title = "error";
    }};

    rec.start();
</script>
</body>
</html>
"""

VOICE_HTML.write_text(HtmlCode, encoding="utf-8")
VoicePage = f"file:///{VOICE_HTML.absolute()}"
print("Voice HTML Ready")

# ================== DRIVER ==================
def CreateDriver():
    options = Options()
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=800,600")
    options.add_argument("--log-level=3")
    options.add_argument("--use-fake-ui-for-media-stream")
    options.add_experimental_option("excludeSwitches", ["enable-logging"])

    return webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )

driver = None

# ================== CLEAN ==================
def CleanQuery(text: str):
    return text.lower().strip()

# ================== TRANSLATE TO ENGLISH ==================
def TranslateToEnglish(text: str):
    try:
        if not text.strip():
            return ""
        # 🔥 FORCE Hindi → English
        return mt.translate(text, "en", "hi").lower().strip()
    except:
        return text.lower().strip()

# ================== SPEECH ==================
def SpeechRecognition(timeout=6):
    global driver

    try:
        if driver is None:
            driver = CreateDriver()
        driver.get(VoicePage)
    except:
        try:
            driver.quit()
        except:
            pass
        driver = CreateDriver()
        driver.get(VoicePage)

    start_time = time.time()

    while time.time() - start_time < timeout:
        try:
            spoken = driver.title.strip()
        except:
            return ""

        # 🔥 VALID SPEECH
        if spoken not in ["LISTENING", "error", ""] and len(spoken) > 1:

            # 🔥 ALWAYS RETURN ENGLISH
            if InputLanguage.startswith("hi"):
                return TranslateToEnglish(spoken)

            return CleanQuery(spoken)

        time.sleep(0.1)

    return ""

# ================== TEST ==================
if __name__ == "__main__":
    print("\n🎤 Speak Hindi or English...\n")

    while True:
        try:
            text = SpeechRecognition()
            if text:
                print("You:", text)

        except KeyboardInterrupt:
            print("\nStopped")
            try:
                driver.quit()
            except:
                pass
            break