from groq import Groq
from json import load, dump
import datetime
from dotenv import dotenv_values
from pathlib import Path
import os

# ------------------ LOAD .env ------------------
BASE_DIR = Path(__file__).resolve().parent.parent
env_vars = dotenv_values(BASE_DIR / ".env")

Username = env_vars.get("USERNAME", "User")
Assistantname = env_vars.get("ASSISTANT_NAME", "Jarvis")
GroqAPIKey = env_vars.get("GROQ_API_KEY")

print("Groq Key Loaded:", GroqAPIKey is not None)
if not GroqAPIKey:
    raise Exception("GROQ_API_KEY missing")

client = Groq(api_key=GroqAPIKey)

# ------------------ SYSTEM PROMPTS ------------------
SYSTEM_NORMAL = f"""
You are {Assistantname}, a voice assistant.
Rules:
- Call user {Username}
- Keep answers short (2-4 lines)
- No greetings unless user greets first
- Do not hallucinate actions
- Follow commands directly
"""

SYSTEM_EXPLAIN = f"""
You are {Assistantname}, a calm teacher.
Explain step by step using simple English.
Provide clarity and examples.
"""

SYSTEM_CODE = f"""
You are {Assistantname}, a professional coder.
Rules:
- Output ONLY code
- No explanation
"""

# ------------------ CHAT LOG ------------------
os.makedirs("Data", exist_ok=True)

try:
    with open("Data/ChatLog.json", "r", encoding="utf-8") as f:
        messages = load(f)
except:
    messages = []
    with open("Data/ChatLog.json", "w", encoding="utf-8") as f:
        dump([], f)

# ------------------ UTILS ------------------
def is_time_query(q: str):
    q = q.lower()
    return any(x in q for x in ["what time", "current time", "time now"])

def AnswerModifier(text: str):
    return "\n".join(line.strip() for line in text.splitlines() if line.strip())

# ================= CHATBOT =================
def ChatBot(query: str, mode="normal"):
    try:
        if is_time_query(query):
            return f"The time is {datetime.datetime.now().strftime('%H:%M:%S')}"

        if mode == "explain":
            system = SYSTEM_EXPLAIN
            chat = []

        elif mode == "code":
            system = SYSTEM_CODE
            chat = []

        else:
            system = SYSTEM_NORMAL
            chat = messages[-12:]

        chat.append({"role": "user", "content": query})

        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "system", "content": system}] + chat,
            temperature=0.4,
            max_tokens=700,
            stream=True
        )

        reply = ""
        for chunk in completion:
            if chunk.choices and chunk.choices[0].delta.content:
                reply += chunk.choices[0].delta.content

        final = AnswerModifier(reply)

        if mode == "normal":
            messages.append({"role": "user", "content": query})
            messages.append({"role": "assistant", "content": final})

            with open("Data/ChatLog.json", "w", encoding="utf-8") as f:
                dump(messages[-50:], f, indent=4)

        return final

    except Exception as e:
        print("ChatBot Error:", e)
        return "Something went wrong."

# ------------------ TEST ------------------
if __name__ == "__main__":
    while True:
        user = input(f"{Username}: ")
        print(ChatBot(user))