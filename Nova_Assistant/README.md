# ⚡ Nova — AI Assistant

A modern, voice-enabled AI assistant built with Love by Rohit.
Ask questions, search the web, open websites, and get spoken responses — right in your browser.

🚀 Developed by Rohit Arabale

---

## 🚀 Quick Start

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the app
```bash
python app.py
```

### 3. Open your browser
```
http://127.0.0.1:5000
```

---

## 🎯 Features

| Command Example                    | What It Does                        |
|------------------------------------|-------------------------------------|
| `search web python tutorials`      | Opens Google search in browser      |
| `search wikipedia Albert Einstein` | Reads Wikipedia summary aloud       |
| `open youtube`                     | Opens YouTube in a new tab          |
| `open github`                      | Opens GitHub                        |
| `what time is it`                  | Tells current time (voice + text)   |
| `what is today's date`             | Tells today's date                  |
| `tell me a joke`                   | Tells a programmer joke             |
| `hello` / `hi`                     | Greets you back                     |
| `help`                             | Lists all capabilities              |

### Advanced commands

| Command Example                         | What It Does                         |
|-----------------------------------------|--------------------------------------|
| `what is artificial intelligence`        | Answers basic study/general questions |
| `calculate 25 plus 17`                  | Solves simple math                   |
| `convert 5 km to m`                     | Converts common units                |
| `search youtube flask tutorial`          | Opens a YouTube search               |
| `maps pune railway station`              | Opens Google Maps search             |
| `remember my exam is Monday`             | Saves a persistent note              |
| `show notes`                            | Lists saved notes                    |
| `add todo revise Python`                | Adds a persistent todo               |
| `list todos`                            | Lists todos                          |
| `complete todo 1`                       | Removes a completed todo             |
| `generate password 16`                  | Creates a random password            |
| `roll 2 dice`                           | Rolls dice                           |
| `flip a coin`                           | Chooses heads or tails               |
| `uppercase nova assistant`              | Transforms text                      |
| `count words Nova is very useful`        | Counts words                         |
| `python study plan`                     | Gives a short learning plan          |

### Websites you can open
youtube, google, github, gmail, twitter, instagram, facebook, linkedin,
reddit, netflix, amazon, stackoverflow, wikipedia, maps, news, chatgpt,
whatsapp, translate, drive, docs, sheets, classroom, meet, calendar,
canva, figma, notion, spotify, flipkart, leetcode, w3schools, codepen,
replit, and more.

---

## 📁 Project Structure

```
Nova_Assistant/
├── app.py                  ← Flask app (main entry point)
├── requirements.txt        ← Python dependencies
├── assistant/
│   ├── __init__.py
│   ├── commands.py         ← All command handlers
│   ├── speak.py            ← Text-to-speech module
│   └── utils.py            ← Time/date helpers
├── templates/
│   └── index.html          ← Chat web interface
└── static/
    └── style.css           ← Dark theme styles
```

---

## 🔧 How Voice Works

**Server-side (terminal):** `pyttsx3` speaks responses through your system speakers when running `app.py`.

**Browser-side:** The Web Speech API (`SpeechSynthesis`) speaks responses aloud in your browser — no extra install needed.

**Mic input:** Click the 🎤 button in the browser to speak your query (requires browser microphone permission).

---

## 📦 Dependencies

- `flask` — Web framework
- `pyttsx3` — Offline text-to-speech (terminal)
- `wikipedia` — Wikipedia search

---

## 🐛 Common Issues

| Problem | Fix |
|---|---|
| `ModuleNotFoundError: flask` | Run `pip install flask` |
| `ModuleNotFoundError: wikipedia` | Run `pip install wikipedia` |
| No voice in browser | Allow microphone/audio in browser settings |
| Port already in use | Change port in `app.py`: `port=5001` |


## About
Nova is an AI-powered assistant project.

## Author
Rohit Arabale
