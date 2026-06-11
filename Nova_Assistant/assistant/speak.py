# speak.py — Text-to-speech module for Nova Assistant
# Uses pyttsx3 for offline, cross-platform voice output.
# The engine is initialized lazily (only when needed) to avoid
# crashes when imported in environments without audio (e.g., servers).

import pyttsx3
import threading
import time
import re

_engine = None           # Lazy-loaded engine instance
_engine_lock = threading.Lock()   # Guards engine access across threads
_speak_enabled = True    # Global mute toggle
_speak_log: list[str] = []        # History of all spoken lines


# ──────────────────────────────────────────────
# Engine initialisation (unchanged core logic)
# ──────────────────────────────────────────────

def _get_engine():
    """Initialize the TTS engine only once and return it."""
    global _engine
    if _engine is None:
        try:
            _engine = pyttsx3.init()
            _engine.setProperty('rate', 165)       # Speaking speed (words/min)
            _engine.setProperty('volume', 1.0)     # Max volume
            # Prefer a female voice if available
            voices = _engine.getProperty('voices')
            if len(voices) > 1:
                _engine.setProperty('voice', voices[1].id)
        except Exception as e:
            print(f"[Nova] TTS engine init failed: {e}")
    return _engine


# ──────────────────────────────────────────────
# Core speak function (original, preserved)
# ──────────────────────────────────────────────

def speak(text: str) -> str:
    """
    Print text to console AND speak it aloud.
    Returns the text so callers can use the return value.
    """
    print(f"Nova: {text}")
    _speak_log.append(text)

    if not _speak_enabled:
        return text

    engine = _get_engine()
    if engine:
        try:
            engine.say(text)
            engine.runAndWait()
        except Exception as e:
            print(f"[Nova] TTS error: {e}")
    return text


# ──────────────────────────────────────────────
# Voice / engine configuration
# ──────────────────────────────────────────────

def set_rate(rate: int) -> None:
    """Set the speaking rate (words per minute).

    Typical range is 100–250. Default Nova rate is 165.

    Args:
        rate: Desired speaking speed in words per minute.
    """
    if not isinstance(rate, int) or rate <= 0:
        raise ValueError("rate must be a positive integer.")
    engine = _get_engine()
    if engine:
        engine.setProperty('rate', rate)


def set_volume(volume: float) -> None:
    """Set the TTS volume.

    Args:
        volume: A float between 0.0 (silent) and 1.0 (maximum).
    """
    if not (0.0 <= volume <= 1.0):
        raise ValueError("volume must be between 0.0 and 1.0.")
    engine = _get_engine()
    if engine:
        engine.setProperty('volume', volume)


def set_voice_by_index(index: int) -> bool:
    """Switch to a voice by its index in the system voice list.

    Args:
        index: Zero-based index of the desired voice.

    Returns:
        True if the voice was set successfully, False otherwise.
    """
    engine = _get_engine()
    if engine:
        voices = engine.getProperty('voices')
        if 0 <= index < len(voices):
            engine.setProperty('voice', voices[index].id)
            return True
        print(f"[Nova] Voice index {index} out of range (0–{len(voices) - 1}).")
    return False


def list_voices() -> list[str]:
    """Return a list of available voice names on this system.

    Returns:
        A list of voice name strings, or an empty list if unavailable.
    """
    engine = _get_engine()
    if engine:
        return [v.name for v in engine.getProperty('voices')]
    return []


def get_current_settings() -> dict:
    """Return the current TTS engine settings as a dictionary.

    Returns keys: rate, volume, voice_name, muted.
    """
    engine = _get_engine()
    if engine:
        voices = engine.getProperty('voices')
        current_voice_id = engine.getProperty('voice')
        voice_name = next(
            (v.name for v in voices if v.id == current_voice_id),
            "Unknown"
        )
        return {
            "rate": engine.getProperty('rate'),
            "volume": engine.getProperty('volume'),
            "voice_name": voice_name,
            "muted": not _speak_enabled,
        }
    return {}


# ──────────────────────────────────────────────
# Mute / unmute controls
# ──────────────────────────────────────────────

def mute() -> None:
    """Silence all spoken output. Console printing still works."""
    global _speak_enabled
    _speak_enabled = False


def unmute() -> None:
    """Re-enable spoken output after a mute."""
    global _speak_enabled
    _speak_enabled = True


def is_muted() -> bool:
    """Return True if TTS output is currently muted."""
    return not _speak_enabled


# ──────────────────────────────────────────────
# Convenience speak variants
# ──────────────────────────────────────────────

def speak_lines(lines: list[str], pause: float = 0.0) -> None:
    """Speak a list of strings one by one, with an optional pause between them.

    Args:
        lines: List of text strings to speak in order.
        pause: Seconds to wait between each line (default 0).
    """
    for line in lines:
        speak(line)
        if pause > 0:
            time.sleep(pause)


def speak_async(text: str) -> threading.Thread:
    """Speak text in a background thread so the caller is not blocked.

    Args:
        text: The text to speak aloud.

    Returns:
        The Thread object (already started) so callers can join if needed.
    """
    t = threading.Thread(target=speak, args=(text,), daemon=True)
    t.start()
    return t


def speak_slowly(text: str, rate: int = 110) -> str:
    """Speak text at a slower rate, then restore the previous rate.

    Useful for important announcements or accessibility.

    Args:
        text: The text to speak.
        rate: Speaking rate to use (default 110 wpm).

    Returns:
        The spoken text.
    """
    engine = _get_engine()
    if engine:
        original_rate = engine.getProperty('rate')
        set_rate(rate)
        result = speak(text)
        set_rate(original_rate)
        return result
    return speak(text)


def speak_with_prefix(prefix: str, text: str) -> str:
    """Speak a prefixed announcement, e.g. speak_with_prefix('Warning', 'Low battery').

    Formats as '<PREFIX>: <text>' both on console and aloud.

    Args:
        prefix: Short label shown/spoken before the main text.
        text:   The main message.

    Returns:
        The combined spoken string.
    """
    return speak(f"{prefix}: {text}")


# ──────────────────────────────────────────────
# Speech log
# ──────────────────────────────────────────────

def get_speak_log() -> list[str]:
    """Return the full list of all texts passed to speak() this session."""
    return list(_speak_log)


def clear_speak_log() -> None:
    """Clear the in-memory speech log."""
    _speak_log.clear()


def get_last_spoken() -> str | None:
    """Return the most recently spoken string, or None if nothing has been spoken."""
    return _speak_log[-1] if _speak_log else None


# ──────────────────────────────────────────────
# Text pre-processing helpers
# ──────────────────────────────────────────────

def _strip_markup(text: str) -> str:
    """Remove basic HTML/Markdown tags before speaking.

    Strips tags like <b>, </b>, *bold*, _italic_ so the engine
    does not read them aloud.
    """
    text = re.sub(r'<[^>]+>', '', text)          # HTML tags
    text = re.sub(r'[*_`#]+', '', text)          # Markdown symbols
    return text.strip()


def speak_clean(text: str) -> str:
    """Strip markup from *text* then speak it.

    Useful when Nova's text may contain HTML or Markdown formatting.

    Args:
        text: Raw text that may contain markup.

    Returns:
        The cleaned text that was spoken.
    """
    cleaned = _strip_markup(text)
    return speak(cleaned)


# ──────────────────────────────────────────────
# Engine lifecycle
# ──────────────────────────────────────────────

def shutdown() -> None:
    """Stop and release the TTS engine.

    Call this on application exit to free audio resources cleanly.
    After shutdown, the next call to speak() will reinitialise the engine.
    """
    global _engine
    if _engine is not None:
        try:
            _engine.stop()
        except Exception:
            pass
        _engine = None