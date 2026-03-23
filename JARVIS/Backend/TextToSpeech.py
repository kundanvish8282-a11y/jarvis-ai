import asyncio
import edge_tts
import pygame
import os
import time
from dotenv import dotenv_values
from pathlib import Path
import threading

# ================== LOAD ENV ==================
BASE_DIR = Path(__file__).resolve().parent.parent
env = dotenv_values(BASE_DIR / ".env")

VOICE = env.get("AssistantVoice", "en-CA-LiamNeural")
AUDIO_DIR = BASE_DIR / "Data"
AUDIO_FILE = AUDIO_DIR / "speech.mp3"

# ================== STATE ==================
STOP_SPEECH = False
SPEECH_LOCK = threading.Lock()

# ================== STOP ==================
def StopSpeech():
    global STOP_SPEECH
    STOP_SPEECH = True
    try:
        if pygame.mixer.get_init():
            pygame.mixer.music.stop()
            pygame.mixer.quit()
    except:
        pass
    print("🛑 Voice Stopped")

# ================== TTS GENERATION ==================
async def _generate_tts(text: str):
    if not text.strip():
        return

    AUDIO_DIR.mkdir(exist_ok=True)

    communicate = edge_tts.Communicate(
        text=text,
        voice=VOICE,
        rate="+12%",
        pitch="+5Hz"
    )
    await communicate.save(str(AUDIO_FILE))

def _run_async(coro):
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running():
        asyncio.run_coroutine_threadsafe(coro, loop).result()
    else:
        asyncio.run(coro)

# ================== PLAY AUDIO ==================
def _play_audio():
    global STOP_SPEECH

    if STOP_SPEECH:
        return

    pygame.mixer.init()
    pygame.mixer.music.load(str(AUDIO_FILE))
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy():
        if STOP_SPEECH:
            pygame.mixer.music.stop()
            break
        time.sleep(0.05)

    pygame.mixer.quit()

# ================== MAIN API ==================
def TextToSpeech(text: str):
    global STOP_SPEECH

    if not text or not text.strip():
        return

    with SPEECH_LOCK:
        STOP_SPEECH = False

        try:
            _run_async(_generate_tts(text))

            if not AUDIO_FILE.exists():
                return

            _play_audio()

        except Exception as e:
            print("TTS Error:", e)

        finally:
            try:
                if AUDIO_FILE.exists():
                    AUDIO_FILE.unlink()
            except:
                pass

# ================== TEST ==================
if __name__ == "__main__":
    print("Voice Ready. Type text:")
    while True:
        try:
            TextToSpeech(input("> "))
        except KeyboardInterrupt:
            StopSpeech()
            break