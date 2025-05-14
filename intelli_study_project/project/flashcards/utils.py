# utils.py

import json
import os
import base64
from pathlib import Path

def save_flashcards_to_json(flashcards, filename="flashcards.json"):
    """Save a list of flashcards to a JSON file."""
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(flashcards, f, indent=2)
    return f"✅ Saved to {filename}"

def load_flashcards_from_json(filename="flashcards.json"):
    """Load flashcards from a JSON file."""
    if not os.path.exists(filename):
        return []
    with open(filename, "r", encoding="utf-8") as f:
        return json.load(f)

def format_flashcard(card, show_answer=False):
    """Format a flashcard for display."""
    if show_answer:
        return f"Q: {card['question']}\nA: {card['answer']}"
    return f"Q: {card['question']}"

def image_to_base64(image_path):
    """Convert an image to a base64 string (for future image support)."""
    if not os.path.exists(image_path):
        return None
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode("utf-8")

def ensure_dir(path):
    """Ensure a directory exists."""
    Path(path).mkdir(parents=True, exist_ok=True)
