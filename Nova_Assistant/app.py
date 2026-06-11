# app.py — Nova Assistant Flask Web Application
# This is the main entry point. Run with: python app.py
# Project: Nova AI Assistant
# Developer: Rohit Arabale
#
# FIX: The original HTML had markdown code fences (```) inside the HTML
#      which broke rendering completely. Fixed in index.html.
# FIX: speak() in commands was called but return value was discarded —
#      now all commands return the spoken text so Flask can send it back.
# UPGRADE: Better command routing, smarter matching, cleaner structure.

from flask import Flask, render_template, request, jsonify
from assistant.commands import (
    search_wikipedia,
    open_website,
    search_web,
    tell_time,
    tell_date,
    basic_chat,
    answer_basic_question,
    handle_advanced_command,
    unknown_command,
    greet_user,
    WEBSITES,
)

# Initialize Flask app
app = Flask(__name__)


def process_command(command: str) -> str:
    """
    Route a user command string to the correct handler function.
    Returns the assistant's text response.
    """
    if not command or not command.strip():
        return "Please type something. I'm listening!"

    command = command.lower().strip()

    # --- Advanced utilities: notes, todos, conversions, YouTube, Maps, dice, etc. ---
    advanced_response = handle_advanced_command(command)
    if advanced_response:
        return advanced_response

    # --- Wikipedia search ---
    if "wikipedia" in command or command.startswith("wiki "):
        query = (command
                 .replace("search wikipedia", "")
                 .replace("wikipedia", "")
                 .replace("wiki", "")
                 .strip())
        return search_wikipedia(query)

    # --- Web search ---
    elif command.startswith("search") or command.startswith("google ") or command.startswith("find "):
        query = (command
                 .replace("search web", "")
                 .replace("search for", "")
                 .replace("search", "")
                 .replace("google", "")
                 .replace("find", "")
                 .strip())
        return search_web(query)

    # --- Open website ---
    elif command.startswith("open ") or any(site in command for site in WEBSITES):
        return open_website(command)

    # --- Time ---
    elif any(w in command for w in ["what time", "current time", "tell me the time", "time is it"]):
        return tell_time()

    # --- Date ---
    elif any(w in command for w in ["what date", "today's date", "today date", "what day", "date today"]):
        return tell_date()

    # --- Greeting / chat ---
    elif any(w in command for w in ["hello", "hi", "hey", "how are you", "thank",
                                     "bye", "goodbye", "who are you", "your name",
                                     "what can you do", "help", "joke", "riddle",
                                     "fact", "motivate", "motivation"]):
        return basic_chat(command)

    # --- Basic questions / knowledge / simple math ---
    elif answer_basic_question(command):
        return basic_chat(command)

    # --- Unknown ---
    else:
        return unknown_command()


# ─── Routes ───────────────────────────────────────────────────────────────────

@app.route("/")
def home():
    """Serve the main chat page."""
    return render_template("index.html")


@app.route("/process", methods=["POST"])
def process():
    """
    Receive a JSON POST with {"message": "..."} from the frontend.
    Returns {"response": "..."} with Nova's reply.
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"response": "I received an empty request."}), 400

        user_input = data.get("message", "").strip()
        response_text = process_command(user_input)
        return jsonify({"response": response_text})

    except Exception as e:
        print(f"[Nova] Error processing request: {e}")
        return jsonify({"response": "Sorry, something went wrong on my end. Please try again."}), 500


# ─── Entry Point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("\n" + "=" * 55)
    print("  🤖  NOVA — AI Assistant by Rohit Arabale is starting up...")
    print("=" * 55)
    print("  ➤  Open your browser: http://127.0.0.1:5000")
    print("  ➤  Press CTRL+C to stop the server")
    print("=" * 55 + "\n")
    app.run(debug=True, host="0.0.0.0", port=5000)
