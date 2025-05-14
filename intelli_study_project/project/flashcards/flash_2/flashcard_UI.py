# flashcard_UI.py

import gradio as gr
import time
from flashcard import generate_flashcards
from utils import save_flashcards_to_json, load_flashcards_from_json

flashcards = []
index = 0

def upload_text(text):
    global flashcards, index
    flashcards = generate_flashcards(text)
    index = 0
    if not flashcards:
        return "⚠️ No valid flashcards generated. Please check your input format.", "", "", gr.update(visible=False)
    return flashcards[0]['question'], "", flashcards[0]['difficulty'], gr.update(visible=True)

def show_next_card():
    global index
    index += 1
    if index < len(flashcards):
        return flashcards[index]['question'], "", flashcards[index]['difficulty'], gr.update(visible=True)
    else:
        return "✅ Done!", "", "", gr.update(visible=False)

def reveal_answer():
    if index < len(flashcards):
        return flashcards[index]['answer']
    return ""

with gr.Blocks(css="style.css") as demo:
    gr.Markdown("# 🧠 Advanced Flashcard App with Timer, Code & Difficulty Level")

    with gr.Row():
        input_text = gr.Textbox(label="Paste Topics (e.g., Term: Definition or Code)", lines=10)
        upload_btn = gr.Button("Generate Flashcards")

    card_display = gr.Textbox(label="Question / Term", lines=3, interactive=False)
    card_back = gr.Textbox(label="Answer", lines=6, interactive=False)
    difficulty_display = gr.Textbox(label="Difficulty", interactive=False)

    with gr.Row(visible=False) as buttons:
        next_btn = gr.Button("Next")
        save_btn = gr.Button("💾 Save Flashcards")

    def generate_flashcard_and_timer(text):
        question, _, difficulty, _ = upload_text(text)
        for i in range(30, 0, -1):
            yield question, f"⏳ Revealing in {i}s...", difficulty, gr.update(visible=True)
            time.sleep(1)
        yield question, reveal_answer(), difficulty, gr.update(visible=True)

    def next_flashcard():
        q, _, diff, btns = show_next_card()
        for i in range(30, 0, -1):
            yield q, f"⏳ Revealing in {i}s...", diff, btns
            time.sleep(1)
        yield q, reveal_answer(), diff, btns

    upload_btn.click(fn=generate_flashcard_and_timer, inputs=input_text, outputs=[card_display, card_back, difficulty_display, buttons])
    next_btn.click(fn=next_flashcard, outputs=[card_display, card_back, difficulty_display, buttons])
    save_btn.click(fn=lambda: save_flashcards_to_json(flashcards), outputs=card_back)

demo.launch()
