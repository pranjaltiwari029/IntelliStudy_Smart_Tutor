import gradio as gr
import time
from flashcard import generate_flashcards_from_text
from utils import save_flashcards_to_json

flashcards = []
index = 0

def upload_text(text):
    global flashcards, index
    flashcards = generate_flashcards_from_text(text)
    index = 0
    return flashcards[0]['question'], "", gr.update(visible=True), gr.update(visible=True)

def reveal_answer():
    if index < len(flashcards):
        return flashcards[index]['answer']
    return ""

def show_next_card():
    global index
    index += 1
    if index < len(flashcards):
        return flashcards[index]['question'], "", gr.update(visible=True)
    else:
        return "✅ Done!", "", gr.update(visible=False)

with gr.Blocks(css="style.css") as demo:
    gr.Markdown("# ⏱️ Timed Flashcard Generator")

    with gr.Row():
        input_text = gr.Textbox(label="Paste Text or Concepts (e.g., Term: Definition)", lines=10)
        upload_btn = gr.Button("Generate Flashcards")

    card_display = gr.Textbox(label="Question / Term", lines=2, interactive=False)
    card_back = gr.Textbox(label="Answer", lines=2, interactive=False)

    with gr.Row(visible=False) as buttons:
        next_btn = gr.Button("Next")
        save_btn = gr.Button("💾 Save Flashcards")

    def generate_flashcard_and_timer(text):
        question, _, btns, save_visible = upload_text(text)
        for i in range(30, 0, -1):
            yield question, f"⏳ Showing answer in {i} sec...", btns, save_visible
            time.sleep(1)
        yield question, reveal_answer(), btns, save_visible

    def next_flashcard():
        q, _, btns = show_next_card()
        for i in range(30, 0, -1):
            yield q, f"⏳ Showing answer in {i} sec...", btns, gr.update(visible=True)
            time.sleep(1)
        yield q, reveal_answer(), btns, gr.update(visible=True)

    upload_btn.click(fn=generate_flashcard_and_timer, inputs=input_text,
                     outputs=[card_display, card_back, buttons, save_btn])
    next_btn.click(fn=next_flashcard,
                   outputs=[card_display, card_back, buttons, save_btn])
    save_btn.click(fn=lambda: save_flashcards_to_json(flashcards), outputs=card_back)

demo.launch()
