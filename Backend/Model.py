from groq import Groq
from dotenv import dotenv_values
from pathlib import Path
from rich import print

# ------------------ LOAD ENV ------------------
BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"

env_vars = dotenv_values(ENV_PATH)
GROQ_API_KEY = env_vars.get("GROQ_API_KEY")

print("Groq Key Loaded:", bool(GROQ_API_KEY))
if not GROQ_API_KEY:
    raise Exception("GROQ_API_KEY not found in .env")

# ------------------ GROQ CLIENT ------------------
client = Groq(api_key=GROQ_API_KEY)
print("Groq client ready ✅")

# ------------------ VALID COMMANDS ------------------
VALID_COMMANDS = [
    "stop", "write", "write_text", "explain", "general", "realtime",
    "open", "close", "play", "generate image", "system",
    "content", "google search", "youtube search",
    "message", "send"
]

# ------------------ PREAMBLE ------------------
PREAMBLE = """
Convert user input into commands only.
No explanation.
Only commands.
"""

# ================= DECISION ENGINE =================
def FirstLayerDMM(prompt: str):
    if not prompt or not prompt.strip():
        return []

    p = prompt.lower().strip()

    # ------------------ AUTO FIX ------------------
    CORRECTIONS = {
        "colse": "close",
        "cloze": "close",
        "closs": "close",
        "opne": "open",
        "watsapp": "whatsapp",
        "whatapp": "whatsapp",
        "karo": "",
        "kar": "",
        "ko": ""
    }

    for wrong, correct in CORRECTIONS.items():
        p = p.replace(wrong, correct)

    p = " ".join(p.split())

    # ------------------ STOP ------------------
    if any(w in p for w in ["stop", "cancel", "pause", "quiet"]):
        return ["stop"]

    # =====================================================
    # 🔥 FORCE WHATSAPP OPEN
    # =====================================================
    if "whatsapp" in p and "open" in p and "message" not in p:
        return ["open whatsapp"]

    # =====================================================
    # 🔥 FULL WHATSAPP COMMAND (FINAL FIX)
    # =====================================================
    if "whatsapp" in p and "message" in p:
        try:
            words = p.split()

            name = None
            message = ""

            # 🔥 find contact name
            if "message" in words:
                idx = words.index("message")
                if idx > 0:
                    name = words[idx - 1]

            # 🔥 extract message text
            message_part = p.split("message", 1)[1]

            # remove unwanted words
            for w in ["karo", "kar", "ko"]:
                message_part = message_part.replace(w, "")

            message = message_part.strip()

            # fallback message
            if not message:
                message = "hello"

            return [
                "open whatsapp",
                f"message {name}",
                message,
                "send"
            ]

        except:
            return ["open whatsapp"]

    # ------------------ MESSAGE CONTACT ------------------
    if p.startswith("message "):
        return [p]

    # ------------------ SEND ------------------
    if p == "send":
        return ["send"]

    # ------------------ OPEN ------------------
    if p.startswith("open "):
        return [f"open {p.replace('open', '', 1).strip()}"]

    # ------------------ CLOSE ------------------
    if p.startswith("close "):
        return [f"close {p.replace('close', '', 1).strip()}"]

    # ------------------ YOUTUBE ------------------
    if "youtube" in p:
        if "close" in p:
            return ["close youtube"]
        elif "open" in p:
            return ["open youtube"]

    # ------------------ PLAY ------------------
    if p.startswith("play "):
        return [f"play {prompt[5:]}"]

    # ------------------ WRITE TEXT ------------------
    if "write" in p and "notepad" in p:
        text = p.split("write", 1)[1].strip()
        return ["open notepad", f"write_text {text}"]

    # ------------------ CODE ------------------
    CODE_WORDS = ["html", "css", "js", "python", "java", "c++", "react", "website", "app"]
    if "write" in p and any(w in p for w in CODE_WORDS):
        return [f"write {prompt}"]

    # ------------------ EXPLAIN ------------------
    if "explain" in p:
        return [f"explain {prompt}"]

    # ------------------ GOOGLE ------------------
    if "google" in p:
        topic = p.replace("google", "").strip()
        return [f"google search {topic}"]

    # ------------------ YOUTUBE SEARCH ------------------
    if "youtube search" in p:
        topic = p.replace("youtube search", "").strip()
        return [f"youtube search {topic}"]

    # ------------------ SHORT TEXT = MESSAGE ------------------
    if len(p.split()) <= 6:
        return [p]

    # ------------------ FALLBACK ------------------
    try:
        res = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": PREAMBLE},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            max_tokens=60
        )

        reply = res.choices[0].message.content.strip()

    except Exception as e:
        print("[red]Groq Error:[/red]", e)
        return [f"general {prompt}"]

    cmds = [c.strip() for c in reply.replace("\n", ",").split(",") if c.strip()]

    output = []
    for c in cmds:
        if any(c.startswith(v) for v in VALID_COMMANDS):
            output.append(c)

    return output if output else [f"general {prompt}"]


# ---------------- TEST ------------------
if __name__ == "__main__":
    while True:
        print(FirstLayerDMM(input("\n>>> ")))