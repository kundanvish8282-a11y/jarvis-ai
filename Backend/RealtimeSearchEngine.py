from googlesearch import search
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

print("Groq Key Loaded:", bool(GroqAPIKey))
if not GroqAPIKey:
    raise Exception("GROQ_API_KEY missing")

# ------------------ GROQ CLIENT ------------------
client = Groq(api_key=GroqAPIKey)

# ------------------ SYSTEM PROMPT ------------------
SYSTEM_PROMPT = f"""
You are {Assistantname}, a professional AI assistant.

Rules:
- Answer only what is asked
- Do not invent real-time data
- Use search results ONLY if provided
- Reply in clear professional English
"""

SYSTEM = [{"role": "system", "content": SYSTEM_PROMPT}]

# ------------------ CHAT LOG ------------------
os.makedirs("Data", exist_ok=True)

try:
    with open("Data/ChatLog.json", "r", encoding="utf-8") as f:
        messages = load(f)
except:
    messages = []
    with open("Data/ChatLog.json", "w", encoding="utf-8") as f:
        dump([], f)

# ------------------ GOOGLE SEARCH ------------------
def GoogleSearch(query: str):
    try:
        results = list(search(query, num_results=5))
        if not results:
            return ""
        return "Search results:\n" + "\n".join(f"- {url}" for url in results)
    except Exception:
        return ""

# ------------------ TIME CHECK ------------------
def is_time_query(q: str):
    q = q.lower()
    return any(x in q for x in ["current time", "what time", "time now"])

# ------------------ REALTIME CHATBOT ------------------
def RealtimeSearchEngine(prompt: str):
    global messages

    # ----- HARD TIME HANDLING -----
    if is_time_query(prompt):
        now = datetime.datetime.now()
        return f"The current time is {now.strftime('%H:%M:%S')}."

    messages.append({"role": "user", "content": prompt})
    messages = messages[-20:]  # memory safety

    search_data = GoogleSearch(prompt)

    chat_context = SYSTEM.copy()
    if search_data:
        chat_context.append({"role": "system", "content": search_data})

    chat_context += messages

    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=chat_context,
        temperature=0.6,
        max_tokens=512,
        stream=True
    )

    answer = ""
    for chunk in completion:
        if chunk.choices and chunk.choices[0].delta.content:
            answer += chunk.choices[0].delta.content

    final = answer.strip()

    messages.append({"role": "assistant", "content": final})
    messages = messages[-20:]

    with open("Data/ChatLog.json", "w", encoding="utf-8") as f:
        dump(messages, f, indent=4)

    return final

# ------------------ RUN ------------------
if __name__ == "__main__":
    while True:
        prompt = input(f"{Username}: ")
        print(RealtimeSearchEngine(prompt))