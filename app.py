from flask import Flask, request, jsonify
import os

# import your chatbot logic
from Backend.Chatbot import ChatBot
from Backend.Model import FirstLayerDMM

app = Flask(__name__)

@app.route("/")
def home():
    return "Jarvis AI is running 🚀"

@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json()
    query = data.get("query")

    if not query:
        return jsonify({"error": "No query provided"})

    try:
        decision = FirstLayerDMM(query.lower())

        if decision:
            merged = " ".join(
                cmd.replace("general", "").replace("realtime", "").strip()
                for cmd in decision
                if cmd.startswith(("general", "realtime"))
            )

            if merged:
                answer = ChatBot(merged)
                return jsonify({"response": answer})

        return jsonify({"response": "Command executed"})

    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)