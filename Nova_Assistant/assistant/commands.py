# commands.py — All assistant command handlers for Nova
# Each function handles a specific type of user request.
# FIX: Removed duplicate imports that were scattered mid-file.
# FIX: Added proper return values so Flask can send text back to browser.
# UPGRADE: Added more websites, smarter responses, better error handling.

import ast
import json
import math
import operator
import re
import webbrowser
import random
from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import quote_plus

# Wikipedia is optional — gracefully handle if not installed
try:
    import wikipedia
    WIKIPEDIA_AVAILABLE = True
except ImportError:
    WIKIPEDIA_AVAILABLE = False

from assistant.speak import speak
from assistant.utils import (
    get_current_time,
    get_current_date,
    get_day_name,
    get_time_based_greeting
)

# ─── Greet User ────────────────────────────────────────────────────────────────

def greet_user() -> str:
    """Greet the user based on the time of day."""
    greeting = get_time_based_greeting()
    message = f"{greeting}! I am Nova, your AI assistant. How can I help you today?"
    return speak(message)


# ─── Wikipedia Search ──────────────────────────────────────────────────────────

def search_wikipedia(query: str) -> str:
    """Search Wikipedia and return a short summary."""
    if not query:
        return speak("Please tell me what to search on Wikipedia.")

    if not WIKIPEDIA_AVAILABLE:
        return speak("Wikipedia library is not installed. Run: pip install wikipedia")

    speak(f"Searching Wikipedia for {query}, please wait...")
    try:
        result = wikipedia.summary(query, sentences=3, auto_suggest=True)
        return speak(result)
    except wikipedia.exceptions.DisambiguationError as e:
        msg = f"Multiple results found for {query}. Try being more specific. Options include: {', '.join(e.options[:3])}."
        return speak(msg)
    except wikipedia.exceptions.PageError:
        return speak(f"Sorry, I couldn't find a Wikipedia page for {query}.")
    except Exception as e:
        return speak(f"Something went wrong while searching Wikipedia: {str(e)}")


# ─── Open Websites ─────────────────────────────────────────────────────────────

# Expanded website dictionary — easy to add more!
WEBSITES = {
    "youtube":    ("https://youtube.com",          "Opening YouTube"),
    "google":     ("https://google.com",           "Opening Google"),
    "github":     ("https://github.com",           "Opening GitHub"),
    "gmail":      ("https://mail.google.com",      "Opening Gmail"),
    "twitter":    ("https://twitter.com",          "Opening Twitter"),
    "instagram":  ("https://instagram.com",        "Opening Instagram"),
    "facebook":   ("https://facebook.com",         "Opening Facebook"),
    "linkedin":   ("https://linkedin.com",         "Opening LinkedIn"),
    "reddit":     ("https://reddit.com",           "Opening Reddit"),
    "netflix":    ("https://netflix.com",          "Opening Netflix"),
    "amazon":     ("https://amazon.com",           "Opening Amazon"),
    "stackoverflow": ("https://stackoverflow.com", "Opening Stack Overflow"),
    "wikipedia":  ("https://wikipedia.org",        "Opening Wikipedia"),
    "maps":       ("https://maps.google.com",      "Opening Google Maps"),
    "news":       ("https://news.google.com",      "Opening Google News"),
    "chatgpt":    ("https://chatgpt.com",          "Opening ChatGPT"),
    "whatsapp":   ("https://web.whatsapp.com",     "Opening WhatsApp Web"),
    "translate":  ("https://translate.google.com", "Opening Google Translate"),
    "drive":      ("https://drive.google.com",     "Opening Google Drive"),
    "docs":       ("https://docs.google.com",      "Opening Google Docs"),
    "sheets":     ("https://sheets.google.com",    "Opening Google Sheets"),
    "classroom":  ("https://classroom.google.com", "Opening Google Classroom"),
    "meet":       ("https://meet.google.com",      "Opening Google Meet"),
    "calendar":   ("https://calendar.google.com",  "Opening Google Calendar"),
    "photos":     ("https://photos.google.com",    "Opening Google Photos"),
    "canva":      ("https://canva.com",            "Opening Canva"),
    "figma":      ("https://figma.com",            "Opening Figma"),
    "notion":     ("https://notion.so",            "Opening Notion"),
    "spotify":    ("https://open.spotify.com",     "Opening Spotify"),
    "hotstar":    ("https://www.hotstar.com",      "Opening Disney Plus Hotstar"),
    "flipkart":   ("https://flipkart.com",         "Opening Flipkart"),
    "myntra":     ("https://myntra.com",           "Opening Myntra"),
    "zomato":     ("https://zomato.com",           "Opening Zomato"),
    "swiggy":     ("https://swiggy.com",           "Opening Swiggy"),
    "paytm":      ("https://paytm.com",            "Opening Paytm"),
    "weather":    ("https://weather.com",          "Opening Weather"),
    "speedtest":  ("https://speedtest.net",        "Opening Speedtest"),
    "leetcode":   ("https://leetcode.com",         "Opening LeetCode"),
    "geeksforgeeks": ("https://geeksforgeeks.org", "Opening GeeksforGeeks"),
    "w3schools":  ("https://w3schools.com",        "Opening W3Schools"),
    "codepen":    ("https://codepen.io",           "Opening CodePen"),
    "replit":     ("https://replit.com",           "Opening Replit"),
    # ── New entries ──
    "claude":     ("https://claude.ai",            "Opening Claude"),
    "gemini":     ("https://gemini.google.com",    "Opening Gemini"),
    "perplexity": ("https://perplexity.ai",        "Opening Perplexity"),
    "trello":     ("https://trello.com",           "Opening Trello"),
    "slack":      ("https://app.slack.com",        "Opening Slack"),
    "discord":    ("https://discord.com/app",      "Opening Discord"),
    "medium":     ("https://medium.com",           "Opening Medium"),
    "hashnode":   ("https://hashnode.com",         "Opening Hashnode"),
    "devto":      ("https://dev.to",               "Opening Dev dot to"),
    "producthunt": ("https://producthunt.com",     "Opening Product Hunt"),
    "hackerrank": ("https://hackerrank.com",       "Opening HackerRank"),
    "codeforces": ("https://codeforces.com",       "Opening Codeforces"),
    "kaggle":     ("https://kaggle.com",           "Opening Kaggle"),
    "vercel":     ("https://vercel.com",           "Opening Vercel"),
    "netlify":    ("https://netlify.com",          "Opening Netlify"),
}

def open_website(command: str) -> str:
    """Open a website based on the command keyword."""
    command_lower = command.lower()
    for keyword, (url, message) in WEBSITES.items():
        if keyword in command_lower:
            webbrowser.open(url)
            return speak(message)
    return speak("I don't know that website. Try something like 'open youtube' or 'open github'.")


# ─── Web Search ────────────────────────────────────────────────────────────────

def search_web(query: str) -> str:
    """Open a Google search in the browser."""
    if not query:
        return speak("What would you like me to search for?")
    url = f"https://www.google.com/search?q={quote_plus(query)}"
    webbrowser.open(url)
    return speak(f"Searching the web for: {query}")


def search_youtube(query: str) -> str:
    """Open a YouTube search for a topic."""
    if not query:
        return speak("What should I search on YouTube?")
    webbrowser.open(f"https://www.youtube.com/results?search_query={quote_plus(query)}")
    return speak(f"Searching YouTube for: {query}")


def search_maps(place: str) -> str:
    """Open Google Maps for a place."""
    if not place:
        return speak("Which place should I search on Maps?")
    webbrowser.open(f"https://www.google.com/maps/search/{quote_plus(place)}")
    return speak(f"Opening Maps for: {place}")


def search_github(query: str) -> str:
    """Search GitHub repositories in the browser.

    Args:
        query: Search query string.
    """
    if not query:
        return speak("What should I search on GitHub?")
    webbrowser.open(f"https://github.com/search?q={quote_plus(query)}&type=repositories")
    return speak(f"Searching GitHub for: {query}")


def search_news(query: str) -> str:
    """Search Google News for a topic.

    Args:
        query: News search query.
    """
    if not query:
        return speak("What news topic should I search for?")
    webbrowser.open(f"https://news.google.com/search?q={quote_plus(query)}")
    return speak(f"Searching news for: {query}")


# ─── Time & Date ───────────────────────────────────────────────────────────────

def tell_time() -> str:
    """Tell the current time."""
    time_str = get_current_time()
    return speak(f"The current time is {time_str}.")


def tell_date() -> str:
    """Tell today's date."""
    date_str = get_current_date()
    day_str = get_day_name()
    return speak(f"Today is {day_str}, {date_str}.")


def tell_day_of_week() -> str:
    """Tell what day of the week it is today."""
    return speak(f"Today is {get_day_name()}.")


def days_until(command: str) -> str | None:
    """Tell the number of days until a given date.

    Recognises patterns like 'days until 25 december' or 'how many days until 2025-08-15'.
    """
    text = command.lower()
    if "days until" not in text and "days to" not in text:
        return None

    # Try ISO format first: YYYY-MM-DD
    iso_match = re.search(r"(\d{4}-\d{1,2}-\d{1,2})", text)
    if iso_match:
        try:
            target = datetime.strptime(iso_match.group(1), "%Y-%m-%d")
            delta = (target.date() - datetime.now().date()).days
            if delta < 0:
                return speak(f"That date was {abs(delta)} days ago.")
            return speak(f"There are {delta} days until {target.strftime('%d %B %Y')}.")
        except ValueError:
            pass

    # Try "25 december" / "december 25" style
    months = {
        "january": 1, "february": 2, "march": 3, "april": 4,
        "may": 5, "june": 6, "july": 7, "august": 8,
        "september": 9, "october": 10, "november": 11, "december": 12,
    }
    for month_name, month_num in months.items():
        pattern = rf"(\d{{1,2}})\s+{month_name}|{month_name}\s+(\d{{1,2}})"
        m = re.search(pattern, text)
        if m:
            day = int(m.group(1) or m.group(2))
            now = datetime.now()
            year = now.year if datetime(now.year, month_num, day).date() >= now.date() else now.year + 1
            try:
                target = datetime(year, month_num, day)
                delta = (target.date() - now.date()).days
                return speak(f"There are {delta} days until {target.strftime('%d %B %Y')}.")
            except ValueError:
                return speak("That does not look like a valid date.")

    return speak("Please give me a date like '25 December' or '2025-12-25'.")


# ─── Basic Chat ────────────────────────────────────────────────────────────────

# Lists of varied responses for a more natural conversation
HELLO_RESPONSES = [
    "Hello there! How can I assist you today?",
    "Hey! Great to see you. What can I do for you?",
    "Hi! I'm Nova, ready to help you!",
]

HOW_ARE_YOU_RESPONSES = [
    "I'm doing great, thank you for asking! How can I help you?",
    "Running at full power! What do you need today?",
    "All systems green! What can I help you with?",
]

THANKS_RESPONSES = [
    "You're very welcome! Anything else?",
    "Happy to help! Let me know if you need anything else.",
    "My pleasure! What else can I do for you?",
]

JOKES = [
    "Why do programmers prefer dark mode? Because light attracts bugs!",
    "Why did the developer go broke? Because he used up all his cache!",
    "I would tell you a UDP joke, but you might not get it.",
    "Why was the computer cold? It left its Windows open.",
    "Why do Java developers wear glasses? Because they don't C sharp.",
    "What do you call a fish with no eyes? A fsh.",
    "I'm reading a book about anti-gravity. It's impossible to put down.",
    "Why do cows wear bells? Because their horns don't work.",
]

RIDDLES = [
    "What has keys but can't open locks? A keyboard.",
    "What has hands but cannot clap? A clock.",
    "What gets wetter the more it dries? A towel.",
    "I speak without a mouth and hear without ears. What am I? An echo.",
    "The more you take, the more you leave behind. What am I? Footsteps.",
]

MOTIVATION = [
    "Small progress is still progress. Take one clear step and keep moving.",
    "You do not need to finish everything at once. Start with the next useful action.",
    "Focus for twenty minutes, remove one distraction, and make the work visible.",
    "Every expert was once a beginner. Keep going.",
    "Done is better than perfect. Ship it, then improve it.",
]

TRIVIA = [
    "The first computer bug was an actual bug — a moth found inside a Harvard Mark II computer in 1947.",
    "Python was named after the comedy group Monty Python, not the snake.",
    "The first ever website is still online at info.cern.ch.",
    "A group of flamingos is called a flamboyance.",
    "Bananas are technically berries, but strawberries are not.",
    "The Eiffel Tower grows about 15 cm taller in summer due to thermal expansion.",
    "Octopuses have three hearts and blue blood.",
    "The word 'robot' comes from a Czech word meaning forced labor.",
]

MEMORY_FILE = Path(__file__).resolve().parent.parent / "data" / "nova_memory.json"


def _load_memory() -> dict:
    """Load persistent notes and todos from disk."""
    if not MEMORY_FILE.exists():
        return {"notes": [], "todos": []}
    try:
        with MEMORY_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)
    except (OSError, json.JSONDecodeError):
        return {"notes": [], "todos": []}
    return {
        "notes": list(data.get("notes", [])),
        "todos": list(data.get("todos", [])),
    }


def _save_memory() -> None:
    """Save persistent notes and todos to disk."""
    MEMORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    with MEMORY_FILE.open("w", encoding="utf-8") as file:
        json.dump({"notes": NOTES, "todos": TODO_ITEMS}, file, indent=2)


_MEMORY = _load_memory()
TODO_ITEMS = _MEMORY["todos"]
NOTES = _MEMORY["notes"]

BASIC_QA = {
    ("what is ai", "what is artificial intelligence", "define ai"): "AI means artificial intelligence. It is technology that helps machines perform tasks that usually need human thinking, like understanding language, recognizing images, and making decisions.",
    ("what is computer", "define computer"): "A computer is an electronic machine that takes input, processes data, stores information, and gives output.",
    ("what is internet", "define internet"): "The internet is a worldwide network of connected computers that share information and services.",
    ("what is python", "define python language"): "Python is a popular programming language known for simple syntax. It is used for web apps, automation, data science, AI, and scripting.",
    ("what is flask", "define flask"): "Flask is a lightweight Python web framework used to build websites, APIs, and web applications.",
    ("what is html", "define html"): "HTML stands for HyperText Markup Language. It creates the structure of web pages.",
    ("what is css", "define css"): "CSS stands for Cascading Style Sheets. It controls colors, layout, spacing, fonts, and the visual design of web pages.",
    ("what is javascript", "define javascript", "what is js"): "JavaScript is a programming language used to make websites interactive, such as buttons, forms, animations, and live updates.",
    ("what is api", "define api"): "An API is an Application Programming Interface. It lets two software systems communicate with each other.",
    ("what is database", "define database"): "A database is an organized place to store, manage, and retrieve data.",
    ("what is cloud computing", "define cloud computing"): "Cloud computing means using internet-based servers to store data, run apps, and provide services instead of using only your own computer.",
    ("what is machine learning", "define machine learning"): "Machine learning is a part of AI where computers learn patterns from data and improve at tasks without being directly programmed for every rule.",
    ("what is cyber security", "what is cybersecurity", "define cyber security"): "Cybersecurity is the practice of protecting computers, networks, accounts, and data from attacks or unauthorized access.",
    ("what is operating system", "define operating system", "what is os"): "An operating system is system software that manages hardware, files, memory, apps, and user interaction. Examples include Windows, Linux, Android, and macOS.",
    ("what is cpu", "define cpu"): "CPU stands for Central Processing Unit. It is the main processor that runs instructions in a computer.",
    ("what is ram", "define ram"): "RAM stands for Random Access Memory. It temporarily stores data that the computer is actively using.",
    ("what is rom", "define rom"): "ROM stands for Read Only Memory. It stores permanent instructions needed to start or run a device.",
    ("what is gpu", "define gpu"): "GPU stands for Graphics Processing Unit. It handles graphics and parallel computing tasks, useful for games, design, and AI workloads.",
    ("what is ip address", "define ip address"): "An IP address is a unique address that identifies a device on a network.",
    ("what is url", "define url"): "A URL is a web address that points to a page or resource on the internet.",
    ("what is virus", "computer virus"): "A computer virus is harmful software that can spread between files or systems and damage, steal, or disrupt data.",
    ("what is climate change", "define climate change"): "Climate change means long-term changes in Earth's temperature and weather patterns, mainly driven today by greenhouse gas emissions.",
    ("what is photosynthesis", "define photosynthesis"): "Photosynthesis is the process where green plants use sunlight, carbon dioxide, and water to make food and release oxygen.",
    ("what is gravity", "define gravity"): "Gravity is the force that attracts objects toward each other. On Earth, it pulls objects toward the ground.",
    ("what is democracy", "define democracy"): "Democracy is a system of government where people choose their leaders, usually through voting.",
    ("what is constitution", "define constitution"): "A constitution is a set of basic rules and principles that guide how a country or organization is governed.",
    ("capital of india", "what is the capital of india"): "The capital of India is New Delhi.",
    ("national animal of india",): "The national animal of India is the Bengal tiger.",
    ("national bird of india",): "The national bird of India is the Indian peacock.",
    ("national flower of india",): "The national flower of India is the lotus.",
    ("national game of india",): "India does not have an officially declared national game.",
    ("largest planet", "biggest planet"): "Jupiter is the largest planet in our solar system.",
    ("smallest planet",): "Mercury is the smallest planet in our solar system.",
    ("nearest planet to sun", "closest planet to sun"): "Mercury is the closest planet to the Sun.",
    ("red planet",): "Mars is called the Red Planet.",
    ("who invented computer",): "Charles Babbage is often called the father of the computer because he designed the Analytical Engine.",
    ("who is father of computer",): "Charles Babbage is known as the father of the computer.",
    ("who is father of ai", "father of artificial intelligence"): "John McCarthy is often called the father of artificial intelligence.",
    ("who are you", "your name", "what is your name"): "I am Nova, your personal AI assistant. I can answer basic questions, search the web, open websites, tell time and date, and help with simple study topics.",
    ("who made you", "who created you", "who is your developer"): "I was created by Rohit Arabale as the Nova AI Assistant project.",
    ("what is this project", "about this project", "what is nova"): "Nova is a Flask-based AI assistant project that can chat, answer basic questions, open websites, search the web, and speak responses aloud.",
    # ── New Q&A entries ──
    ("what is blockchain", "define blockchain"): "Blockchain is a distributed digital ledger that records transactions across many computers so that no single party can alter the history.",
    ("what is vpn", "define vpn"): "A VPN, or Virtual Private Network, encrypts your internet connection and hides your IP address to improve privacy and security online.",
    ("what is open source", "define open source"): "Open source means software whose source code is publicly available for anyone to read, modify, and distribute.",
    ("what is git", "define git"): "Git is a version control system that tracks changes in code over time and lets multiple developers collaborate on the same project.",
    ("what is docker", "define docker"): "Docker is a platform that packages applications and their dependencies into containers so they run consistently across different environments.",
    ("what is recursion", "define recursion"): "Recursion is when a function calls itself to solve a smaller version of the same problem, stopping when a base condition is met.",
    ("what is sql", "define sql"): "SQL stands for Structured Query Language. It is used to create, read, update, and delete data in relational databases.",
    ("what is oop", "define oop", "what is object oriented programming"): "Object-oriented programming organises code into classes and objects that bundle data and behaviour together, making large programs easier to manage.",
    ("what is rest api", "define rest api"): "A REST API is a web service that follows the REST design style, using HTTP methods like GET, POST, PUT, and DELETE to exchange data.",
    ("what is debugging", "define debugging"): "Debugging is the process of finding and fixing errors, or bugs, in a program so it runs correctly.",
}

HOW_TO_ANSWERS = {
    "study better": "To study better, make a small timetable, remove distractions, study in focused sessions, revise regularly, and test yourself instead of only reading.",
    "learn programming": "Start with one language like Python, learn the basics, build small projects, read other code, and practice every day.",
    "improve english": "Read daily, listen to clear English, learn five new words at a time, speak simple sentences aloud, and write short paragraphs.",
    "make website": "To make a website, create HTML for structure, CSS for design, JavaScript for interaction, then test it in a browser.",
    "create resume": "A good resume should include your contact details, skills, education, projects, experience if any, and achievements in clear bullet points.",
    "prepare for exam": "Start with the syllabus, mark important chapters, make a timetable, solve previous papers, revise formulas, and sleep properly before the exam.",
    "stay focused": "Keep your phone away, choose one task, set a timer for 25 minutes, and take a short break after finishing that session.",
    # ── New how-to entries ──
    "use git": "To use Git: install it, run git init in your project folder, add files with git add, commit with git commit -m 'message', and push to GitHub with git push.",
    "learn ai": "Start with Python basics, learn NumPy and Pandas for data handling, then study machine learning with scikit-learn, and finally explore deep learning with TensorFlow or PyTorch.",
    "improve typing speed": "Practice on typing websites daily, keep correct posture, avoid looking at the keyboard, start slow and build accuracy before speed.",
    "manage time": "Write your tasks the night before, prioritize by importance, use a timer for focused work, and review your day each evening.",
    "read faster": "Preview headings first, avoid re-reading each line, use your finger as a guide, and practice with slightly challenging material each day.",
}

STUDY_PLANS = {
    "python": "Python study plan: learn variables, conditions, loops, functions, lists, dictionaries, file handling, then build small projects like a calculator, quiz app, and Flask website.",
    "web development": "Web development plan: learn HTML structure, CSS layout, JavaScript basics, responsive design, Git, then build a portfolio, landing page, and small interactive app.",
    "flask": "Flask plan: understand routes, templates, static files, forms, JSON APIs, error handling, then connect a database and deploy a small app.",
    "ai": "AI study plan: learn Python, basic math, data handling, machine learning concepts, model evaluation, then build small projects with real datasets.",
    # ── New study plans ──
    "data science": "Data science plan: learn Python, NumPy, Pandas, data visualisation with Matplotlib, statistics basics, then work through real datasets on Kaggle.",
    "cybersecurity": "Cybersecurity plan: understand networking basics, learn Linux commands, study ethical hacking concepts, practice on platforms like TryHackMe, then earn an entry-level certification.",
    "sql": "SQL study plan: learn SELECT, WHERE, ORDER BY, GROUP BY, JOIN types, subqueries, then practice on a real database project like a student records system.",
    "git": "Git study plan: init, add, commit, push, pull, branching, merging, resolving conflicts, then collaborate on a GitHub project with someone else.",
}

_MATH_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}

# ── Math function map (for expressions like 'sqrt 25' or 'log 100') ──
_MATH_FUNCTIONS = {
    "sqrt": math.sqrt,
    "log": math.log10,
    "sin": lambda x: math.sin(math.radians(x)),
    "cos": lambda x: math.cos(math.radians(x)),
    "tan": lambda x: math.tan(math.radians(x)),
    "abs": abs,
    "ceil": math.ceil,
    "floor": math.floor,
    "factorial": math.factorial,
}


def _normalize(text: str) -> str:
    """Lowercase and remove punctuation so question matching is forgiving."""
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9\s]", " ", text.lower())).strip()


def _safe_eval_math(expression: str):
    """Evaluate only simple arithmetic expressions."""
    def eval_node(node):
        if isinstance(node, ast.Expression):
            return eval_node(node.body)
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return node.value
        if isinstance(node, ast.Num):
            return node.n
        if isinstance(node, ast.BinOp) and type(node.op) in _MATH_OPERATORS:
            return _MATH_OPERATORS[type(node.op)](eval_node(node.left), eval_node(node.right))
        if isinstance(node, ast.UnaryOp) and type(node.op) in _MATH_OPERATORS:
            return _MATH_OPERATORS[type(node.op)](eval_node(node.operand))
        raise ValueError("Unsupported math expression")

    parsed = ast.parse(expression, mode="eval")
    return eval_node(parsed)


def calculate_answer(command: str) -> str | None:
    """Answer simple arithmetic and math function questions.

    Supports standard arithmetic plus sqrt, log, sin, cos, tan, abs,
    ceil, floor, and factorial — e.g. 'sqrt 144' or 'factorial 5'.
    """
    text = command.lower()

    # ── Named math functions first ──
    for fn_name, fn in _MATH_FUNCTIONS.items():
        pattern = rf"\b{fn_name}\s+([\d.]+)"
        m = re.search(pattern, text)
        if m:
            try:
                value = float(m.group(1))
                result = fn(value)
                if isinstance(result, float) and result.is_integer():
                    result = int(result)
                else:
                    result = round(result, 6)
                return f"The {fn_name} of {m.group(1)} is {result}."
            except (ValueError, OverflowError) as e:
                return f"Could not compute {fn_name} of {m.group(1)}: {e}"

    # ── Standard arithmetic ──
    expression = text
    replacements = {
        "what is": "",
        "calculate": "",
        "solve": "",
        "plus": "+",
        "minus": "-",
        "times": "*",
        "multiplied by": "*",
        "x": "*",
        "divided by": "/",
        "over": "/",
        "into": "*",
    }
    for old, new in replacements.items():
        expression = expression.replace(old, new)
    expression = expression.strip()

    if not re.fullmatch(r"[0-9\s\.\+\-\*\/\%\(\)]+", expression):
        return None
    if not re.search(r"[\+\-\*\/\%]", expression):
        return None

    try:
        result = _safe_eval_math(expression)
    except Exception:
        return None

    if isinstance(result, float) and result.is_integer():
        result = int(result)
    return f"The answer is {result}."


def convert_units(command: str) -> str | None:
    """Convert common units without extra dependencies."""
    text = command.lower().strip()
    match = re.search(r"(-?\d+(?:\.\d+)?)\s*(km|kilometer|kilometers|m|meter|meters|cm|centimeter|centimeters|kg|kilogram|kilograms|g|gram|grams|c|celsius|f|fahrenheit|lb|pound|pounds|oz|ounce|ounces|mi|mile|miles|ft|foot|feet|inch|inches|in|l|liter|liters|ml|milliliter|milliliters)\s+(?:to|in)\s+(km|kilometer|kilometers|m|meter|meters|cm|centimeter|centimeters|kg|kilogram|kilograms|g|gram|grams|c|celsius|f|fahrenheit|lb|pound|pounds|oz|ounce|ounces|mi|mile|miles|ft|foot|feet|inch|inches|in|l|liter|liters|ml|milliliter|milliliters)", text)
    if not match:
        return None

    value = float(match.group(1))
    source = match.group(2)
    target = match.group(3)

    aliases = {
        "kilometer": "km", "kilometers": "km",
        "meter": "m", "meters": "m",
        "centimeter": "cm", "centimeters": "cm",
        "kilogram": "kg", "kilograms": "kg",
        "gram": "g", "grams": "g",
        "celsius": "c", "fahrenheit": "f",
        "pound": "lb", "pounds": "lb",
        "ounce": "oz", "ounces": "oz",
        "mile": "mi", "miles": "mi",
        "foot": "ft", "feet": "ft",
        "inch": "in", "inches": "in",
        "liter": "l", "liters": "l",
        "milliliter": "ml", "milliliters": "ml",
    }
    source = aliases.get(source, source)
    target = aliases.get(target, target)

    conversions = {
        # Length
        ("km", "m"): value * 1000,
        ("m", "km"): value / 1000,
        ("m", "cm"): value * 100,
        ("cm", "m"): value / 100,
        ("km", "cm"): value * 100000,
        ("cm", "km"): value / 100000,
        ("mi", "km"): value * 1.60934,
        ("km", "mi"): value / 1.60934,
        ("mi", "m"): value * 1609.34,
        ("m", "mi"): value / 1609.34,
        ("ft", "m"): value * 0.3048,
        ("m", "ft"): value / 0.3048,
        ("in", "cm"): value * 2.54,
        ("cm", "in"): value / 2.54,
        ("ft", "in"): value * 12,
        ("in", "ft"): value / 12,
        # Mass
        ("kg", "g"): value * 1000,
        ("g", "kg"): value / 1000,
        ("kg", "lb"): value * 2.20462,
        ("lb", "kg"): value / 2.20462,
        ("lb", "oz"): value * 16,
        ("oz", "lb"): value / 16,
        ("kg", "oz"): value * 35.274,
        ("oz", "kg"): value / 35.274,
        # Temperature
        ("c", "f"): (value * 9 / 5) + 32,
        ("f", "c"): (value - 32) * 5 / 9,
        # Volume
        ("l", "ml"): value * 1000,
        ("ml", "l"): value / 1000,
    }

    if source == target:
        result = value
    elif (source, target) in conversions:
        result = conversions[(source, target)]
    else:
        return "I can convert km, meters, centimeters, miles, feet, inches, kg, grams, pounds, ounces, Celsius, Fahrenheit, liters, and milliliters."

    if float(result).is_integer():
        result = int(result)
    else:
        result = round(result, 4)
    return f"{value:g} {source} is {result} {target}."


def generate_password(command: str) -> str | None:
    """Generate a simple random password."""
    if "password" not in command.lower():
        return None
    match = re.search(r"\b(\d{2})\b", command)
    length = int(match.group(1)) if match else 12
    length = max(8, min(length, 32))
    chars = "ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz23456789!@#$%&*"
    password = "".join(random.choice(chars) for _ in range(length))
    return f"Here is a strong {length}-character password: {password}"


def roll_dice(command: str) -> str | None:
    """Roll one or more dice."""
    text = command.lower()
    if "dice" not in text and "die" not in text:
        return None
    match = re.search(r"\b(\d+)\s*dice\b", text)
    count = int(match.group(1)) if match else 1
    count = max(1, min(count, 6))
    rolls = [random.randint(1, 6) for _ in range(count)]
    return f"You rolled: {', '.join(map(str, rolls))}. Total: {sum(rolls)}."


def flip_coin(command: str) -> str | None:
    """Flip a coin."""
    if "coin" in command.lower() or "heads or tails" in command.lower():
        return f"The coin landed on {random.choice(['heads', 'tails'])}."
    return None


def random_number(command: str) -> str | None:
    """Pick a random number within an optional range.

    Recognises phrases like 'random number', 'random number between 1 and 100',
    or 'pick a number from 5 to 50'.
    """
    text = command.lower()
    if "random number" not in text and "pick a number" not in text and "random between" not in text:
        return None

    match = re.search(r"(?:between|from)\s+(\d+)\s+(?:and|to)\s+(\d+)", text)
    if match:
        low, high = int(match.group(1)), int(match.group(2))
        if low > high:
            low, high = high, low
    else:
        low, high = 1, 100

    number = random.randint(low, high)
    return f"Your random number between {low} and {high} is {number}."


def text_tools(command: str) -> str | None:
    """Handle simple text transformations."""
    text = command.strip()
    lowered = text.lower()
    actions = {
        "uppercase ": str.upper,
        "lowercase ": str.lower,
        "count words ": lambda value: f"That text has {len(value.split())} words.",
        "reverse ": lambda value: value[::-1],
        # ── New transformations ──
        "count characters ": lambda value: f"That text has {len(value)} characters.",
        "title case ": str.title,
        "remove spaces ": lambda value: value.replace(" ", ""),
    }
    for prefix, action in actions.items():
        if lowered.startswith(prefix):
            original = text[len(prefix):].strip()
            if not original:
                return "Please give me text to process."
            result = action(original)
            return result if isinstance(result, str) else str(result)
    return None


def memory_tools(command: str) -> str | None:
    """Temporary in-app notes and todo list commands."""
    text = command.strip()
    lowered = text.lower()

    if lowered.startswith(("remember ", "note ")):
        note = re.sub(r"^(remember|note)\s+", "", text, flags=re.IGNORECASE).strip()
        if not note:
            return "Please tell me what to remember."
        NOTES.append(note)
        _save_memory()
        return f"Saved note {len(NOTES)}: {note}"

    if lowered in ["show notes", "list notes", "my notes"]:
        if not NOTES:
            return "You do not have any saved notes yet."
        return "Your notes: " + " | ".join(f"{i + 1}. {note}" for i, note in enumerate(NOTES))

    if lowered in ["clear notes", "delete notes"]:
        NOTES.clear()
        _save_memory()
        return "All notes cleared."

    if lowered.startswith(("add todo ", "todo ", "task ")):
        todo = re.sub(r"^(add todo|todo|task)\s+", "", text, flags=re.IGNORECASE).strip()
        if not todo:
            return "Please tell me the todo item."
        TODO_ITEMS.append(todo)
        _save_memory()
        return f"Added todo {len(TODO_ITEMS)}: {todo}"

    if lowered in ["show todos", "list todos", "my todos", "show tasks", "list tasks"]:
        if not TODO_ITEMS:
            return "Your todo list is empty."
        return "Your todos: " + " | ".join(f"{i + 1}. {todo}" for i, todo in enumerate(TODO_ITEMS))

    if lowered.startswith(("complete todo ", "done todo ", "remove todo ")):
        match = re.search(r"\d+", lowered)
        if not match:
            return "Tell me the todo number to remove, like 'complete todo 1'."
        index = int(match.group()) - 1
        if index < 0 or index >= len(TODO_ITEMS):
            return "I could not find that todo number."
        removed = TODO_ITEMS.pop(index)
        _save_memory()
        return f"Completed todo: {removed}"

    if lowered in ["clear todos", "clear tasks"]:
        TODO_ITEMS.clear()
        _save_memory()
        return "All todos cleared."

    return None


def study_plan(command: str) -> str | None:
    """Return a short learning plan for common topics."""
    normalized = _normalize(command)
    if "study plan" not in normalized and "learning plan" not in normalized:
        return None
    for topic, plan in STUDY_PLANS.items():
        if topic in normalized:
            return plan
    return "A good study plan is: learn basics, practice examples, build a small project, revise weak points, then explain the topic in your own words."


def pick_random_choice(command: str) -> str | None:
    """Pick a random item from a comma-separated list the user provides.

    Recognises: 'choose between pizza, burger, or pasta'
                'pick one from red, blue, green'
    """
    text = command.lower()
    if not any(kw in text for kw in ["choose between", "pick one from", "pick from", "choose from", "which one"]):
        return None

    # Extract content after the trigger phrase
    cleaned = re.sub(r".*(choose between|pick one from|pick from|choose from|which one)\s*", "", text)
    # Split on commas and 'or'
    items = [item.strip().strip("?.,!") for item in re.split(r",|\bor\b", cleaned) if item.strip()]
    if len(items) < 2:
        return None
    chosen = random.choice(items)
    return f"I would go with: {chosen.capitalize()}."


def handle_advanced_command(command: str) -> str | None:
    """Handle utility-style commands before general Q&A fallback."""
    lowered = command.lower().strip()

    if lowered.startswith(("youtube ", "search youtube ", "find on youtube ")):
        query = re.sub(r"^(search youtube|find on youtube|youtube)\s+", "", command, flags=re.IGNORECASE).strip()
        return search_youtube(query)

    if lowered.startswith(("maps ", "map ", "find place ", "search maps ")):
        place = re.sub(r"^(search maps|find place|maps|map)\s+", "", command, flags=re.IGNORECASE).strip()
        return search_maps(place)

    if lowered.startswith(("search github ", "github search ")):
        query = re.sub(r"^(search github|github search)\s+", "", command, flags=re.IGNORECASE).strip()
        return search_github(query)

    if lowered.startswith(("search news ", "news about ", "latest news ")):
        query = re.sub(r"^(search news|news about|latest news)\s+", "", command, flags=re.IGNORECASE).strip()
        return search_news(query)

    # Days until handler
    days_result = days_until(command)
    if days_result:
        return days_result

    handlers = [
        memory_tools,
        convert_units,
        generate_password,
        roll_dice,
        flip_coin,
        random_number,
        pick_random_choice,
        text_tools,
        study_plan,
    ]
    for handler in handlers:
        result = handler(command)
        if result:
            return speak(result)

    return None


def answer_basic_question(command: str) -> str | None:
    """Answer common general-knowledge and study questions."""
    normalized = _normalize(command)

    math_answer = calculate_answer(command)
    if math_answer:
        return math_answer

    conversion_answer = convert_units(command)
    if conversion_answer:
        return conversion_answer

    for questions, answer in BASIC_QA.items():
        if normalized in questions or any(q in normalized for q in questions):
            return answer

    if normalized.startswith("how to ") or normalized.startswith("how can i "):
        for topic, answer in HOW_TO_ANSWERS.items():
            if topic in normalized:
                return answer

    if "motivate" in normalized or "motivation" in normalized or "inspire" in normalized:
        return random.choice(MOTIVATION)

    if "riddle" in normalized:
        return random.choice(RIDDLES)

    if "trivia" in normalized or ("tell me a fact" in normalized and "fact" in normalized):
        return random.choice(TRIVIA)

    if "fact" in normalized:
        facts = [
            "Honey never spoils when stored properly.",
            "The human brain uses about twenty percent of the body's energy.",
            "Light from the Sun takes about eight minutes to reach Earth.",
            "A byte usually contains eight bits.",
        ]
        return random.choice(facts)

    return None


def basic_chat(command: str) -> str:
    """Handle simple conversational inputs."""
    command_lower = command.lower()

    if any(w in command_lower for w in ["hello", "hi", "hey", "greetings"]):
        return speak(random.choice(HELLO_RESPONSES))

    elif "how are you" in command_lower or "how r u" in command_lower:
        return speak(random.choice(HOW_ARE_YOU_RESPONSES))

    elif any(w in command_lower for w in ["thank", "thanks", "thx"]):
        return speak(random.choice(THANKS_RESPONSES))

    elif any(w in command_lower for w in ["bye", "goodbye", "see you", "exit", "quit"]):
        return speak("Goodbye! Have a wonderful day. Come back anytime!")

    elif "your name" in command_lower or "who are you" in command_lower:
        return speak("I am Nova, your personal AI assistant. I can search the web, open websites, tell you the time, and more!")

    elif "what can you do" in command_lower or "help" in command_lower:
        return speak(
            "I can answer basic questions, solve simple math and unit conversions, tell facts and trivia, "
            "give study tips and study plans, search Wikipedia, search the web, search YouTube, search GitHub, "
            "search news, open Maps, open websites, save notes and todos, generate passwords, roll dice, "
            "flip a coin, pick random numbers, choose between options, transform text, tell the time and date, "
            "count days until a date, tell jokes, riddles, and chat with you. "
            "Try: remember my exam is Monday, show notes, add todo revise Python, convert 5 km to m, "
            "search youtube Flask tutorial, generate password 16, sqrt 144, days until 25 december, "
            "or choose between pizza, burger, or pasta."
        )

    elif "joke" in command_lower:
        return speak(random.choice(JOKES))

    basic_answer = answer_basic_question(command)
    if basic_answer:
        return speak(basic_answer)

    else:
        return speak("Hello! How can I help you?")


# ─── Unknown Command ───────────────────────────────────────────────────────────

def unknown_command() -> str:
    """Handle unrecognized commands."""
    suggestions = [
        "I don't know that one yet. Try asking a basic question, saying 'search web' plus your topic, or asking me to open a website.",
        "I could not answer that directly. You can ask things like 'what is AI', 'calculate 25 plus 17', 'open YouTube', or 'search web Python tutorials'.",
        "I am still learning that topic. Say 'help' to see examples, or ask me to search the web for it.",
    ]
    return speak(random.choice(suggestions))