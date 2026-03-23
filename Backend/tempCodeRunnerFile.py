from groq import Groq
from dotenv import dotenv_values
from pathlib import Path

# ------------------ LOAD .env ------------------
BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"

print("Looking for .env at:", ENV_PATH)

env_vars = dotenv_values(ENV_PATH)
GROQ_API_KEY = env_vars.get("GROQ_API_KEY")

print("Groq Key Loaded:", bool(GROQ_API_KEY))
if not GROQ_API_KEY:
    raise Exception("GROQ_API_KEY not found in .env")

# ------------------ GROQ CLIENT ------------------
client = Groq(api_key=GROQ_API_KEY)
print("Groq client created ✅")

# ------------------ ALLOWED COMMANDS ------------------
COMMANDS = [
    "exit",
    "open",
    "close",
    "play",
    "pause",
    "stop",
    "mute",
    "unmute",
    "volume up",
    "volume down",
    "google search",
    "youtube search",
    "send message",
    "whatsapp",
    "telegram"
]

COMMAND_SET = set(COMMANDS)

# ------------------ SYSTEM PROMPT ------------------
SYSTEM_PROMPT = """
You are a command classifier.

STRICT RULES:
- Output ONLY allowed commands
- No explanations
- No extra text
- No punctuation except commas
- If nothing matches, return exactly: general

Allowed commands:
exit, open, close, play, pause, stop,
mute, unmute, volume up, volume down,
google search, youtube search,
send message, whatsapp, telegram

Output format:
comma-separated commands OR general
"""

# ------------------ FUNCTION ------------------
def FirstLayerDMM(user_input: str):
    if not user_input or not user_input.strip():
        return ["general"]

    text_input = user_input.lower().strip()

    # ---- Fast rule-based stop ----
    if text_input in ["stop", "exit", "quit", "close"]:
        return ["stop"] if text_input != "exit" else ["exit"]

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": text_input}
            ],
            temperature=0.0,
            max_tokens=50
        )

        raw = response.choices[0].message.content.lower().strip()
    except Exception as e:
        print("Groq Error:", e)
        return ["general"]

    if raw == "general":
        return ["general"]

    parts = [p.strip() for p in raw.split(",") if p.strip()]
    result = []

    for part in parts:
        if part in COMMAND_SET:
            result.append(part)

    # remove duplicates, preserve order
    result = list(dict.fromkeys(result))

    return result if result else ["general"]

# ------------------ LOOP ------------------
if __name__ == "__main__":
    while True:
        query = input(">>> ")
        print(FirstLayerDMM(query))