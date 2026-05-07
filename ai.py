#!/usr/bin/env python3
import os, json, subprocess, requests, speech_recognition as sr
from datetime import datetime

# ---------------- CONFIG ----------------
BASE_DIR = os.path.expanduser("~/.priya_ai")
CONFIG_FILE = os.path.join(BASE_DIR, "config.json")
MEMORY_FILE = os.path.join(BASE_DIR, "memory.json")
SUMMARY_FILE = os.path.join(BASE_DIR, "summary.txt")

OPENAI_URL = "https://api.openai.com/v1/responses"
MODEL_NAME = "gpt-4.1-mini"
# ----------------------------------------

# ---------- UTILITIES ----------
def speak(text):
    try:
        subprocess.run([
            "termux-tts-speak",
            "-l", "en-US",
            "-v", "en-us-x-sfg#female_2",
            text
        ])
    except:
        pass

def banner():
    print("\033[95m")
    print("======================================")
    print("   😈  PRIYA AI  |  v3.2 Ultimate 😈")
    print("   Boss / GF Mode | Female Voice ❤️")
    print("======================================")
    print("\033[0m")

def load_json(path, default):
    if os.path.exists(path):
        try:
            with open(path) as f:
                return json.load(f)
        except:
            return default
    return default

def save_json(path, data):
    os.makedirs(BASE_DIR, exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

# ---------- API KEY ----------
def load_api_key():
    data = load_json(CONFIG_FILE, {})
    key = data.get("api_key", "").strip()
    return key if key else None

def first_time_setup():
    print("🔐 First Time Setup")
    while True:
        key = input("Enter OpenAI API key: ").strip()
        if key.startswith("sk-"):
            save_json(CONFIG_FILE, {"api_key": key})
            speak("Setup completed Boss Raj")
            break
        else:
            print("❌ Invalid API key. Try again.")

# ---------- MEMORY ----------
def load_memory():
    return load_json(MEMORY_FILE, [])

def save_memory(memory):
    save_json(MEMORY_FILE, memory[-30:])

def update_summary(api_key, memory):
    text = "\n".join([f"{m['role']}: {m['content']}" for m in memory])
    prompt = f"Summarize this conversation briefly:\n{text}"
    summary = ask_openai(api_key, [], prompt)
    with open(SUMMARY_FILE, "w") as f:
        f.write(summary)

def load_summary():
    if os.path.exists(SUMMARY_FILE):
        return open(SUMMARY_FILE).read()
    return ""

# ---------- VOICE INPUT ----------
def listen_voice():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎙️ Listening Boss Raj...")
        audio = r.listen(source)
    try:
        return r.recognize_google(audio)
    except:
        return ""

# ---------- AI ----------
GF_MODE = False

SYSTEM_PROMPT = """
You are PRIYA AI.
Speak naturally, emotionally intelligent, caring.
GF Mode = affectionate girlfriend tone.
Boss Mode = confident assistant.
"""

def ask_openai(api_key, memory, user_text):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages += memory
    messages.append({"role": "user", "content": user_text})

    try:
        r = requests.post(
            OPENAI_URL,
            headers=headers,
            json={"model": MODEL_NAME, "input": messages},
            timeout=30
        )
        return r.json()["output"][0]["content"][0]["text"]
    except:
        return "Boss Raj, mujhe response nahi mila 😔"

# ---------- MAIN ----------
def main():
    global GF_MODE
    banner()

    api_key = load_api_key()
    if not api_key:
        first_time_setup()
        api_key = load_api_key()

    memory = load_memory()
    speak("Priya AI ready Boss Raj")

    while True:
        user = input("\n⌨️ Type / voice / exit > ").strip()

        if user.lower() == "exit":
            speak("Goodbye Boss Raj")
            break

        if user.lower() == "voice":
            user = listen_voice()
            print("🧑 Boss Raj >", user)

        if not user:
            continue

        if "gf mode activate" in user.lower():
            GF_MODE = True
            reply = "GF Mode activated 💖 Ab main tumhari girlfriend hoon."
        elif "gf mode deactivate" in user.lower():
            GF_MODE = False
            reply = "GF Mode off. Back to Boss Mode."
        else:
            print("🤖 Thinking...")
            reply = ask_openai(api_key, memory, user)

        print("😈 Priya >", reply)
        speak(reply)

        memory.append({"role": "user", "content": user})
        memory.append({"role": "assistant", "content": reply})
        save_memory(memory)

if __name__ == "__main__":
    main()
