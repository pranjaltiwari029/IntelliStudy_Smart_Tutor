# ui.py

import gradio as gr
from summarizer import extract_text, detect_sections, summarize_sections
from quiz_generator import generate_mcq_questions_individually, generate_answer_key

# Globals to store state between questions
quiz_questions = []
user_answers = []
correct_answers = []
question_index = 0
study_material = ""


def upload_file(file):
    global study_material, quiz_questions, user_answers, correct_answers, question_index

    file_path = file.name
    study_material = extract_text(file_path)

    sections = detect_sections(study_material)
    summaries = summarize_sections(sections)

    summary_text = "\n\n".join(f"📌 {title}\n{summary}" for title, summary in summaries.items())

    # Reset quiz state
    quiz_questions = []
    user_answers = []
    correct_answers = []
    question_index = 0

    return summary_text, gr.update(visible=True)

def start_quiz():
    global quiz_questions, question_index
    quiz_questions = generate_mcq_questions_individually(study_material)
    question_index = 0
    return quiz_questions[0]

def submit_answer(answer):
    global question_index, user_answers

    user_answers.append(answer)

    question_index += 1
    if question_index < len(quiz_questions):
        return quiz_questions[question_index], ""
    else:
        return "✅ Quiz Complete!", "Click 'Show Score' to view results."

def show_score():
    global correct_answers

    # Get the full answer key
    answer_key = generate_answer_key(study_material, quiz_questions)

    # Split each question block
    correct_blocks = answer_key.strip().split("\n\n")

    result = ""
    score = 0

    for i in range(len(quiz_questions)):
        q_number = i + 1
        user_answer = user_answers[i].strip().upper()

        # Try to find the answer block for this question
        block = next((b for b in correct_blocks if b.startswith(f"Q{q_number}:")), None)
        if not block:
            result += f"\nQ{q_number}:\nYour Answer: {user_answer}\nCorrect Answer: Not found\n❌ Incorrect (Missing data)\n"
            continue

        lines = block.strip().split("\n")
        question_line = lines[0]
        correct_line = next((line for line in lines if line.startswith("Correct Answer:")), "")

        # Extract correct option letter
        correct_letter = correct_line.split("Correct Answer:")[1].strip()[0].upper() if "Correct Answer:" in correct_line else "?"

        is_correct = user_answer == correct_letter
        mark = "✅ Correct" if is_correct else "❌ Incorrect"

        if is_correct:
            score += 1

        result += (
            f"\n{question_line}\n"
            f"Your Answer: {user_answer}\n"
            f"{correct_line}\n"
            f"{mark}\n"
        )

    result += f"\n\n🏁 Final Score: {score} / {len(quiz_questions)}"
    return result




# Gradio Interface

with gr.Blocks() as demo:
    gr.Markdown("# 📘 IntelliStudy: Summarizer & Quiz Generator")

    file_input = gr.File(label="Upload a PDF or DOCX file")
    summary_output = gr.Textbox(label="📄 Summarized Sections", lines=15, interactive=False)
    start_btn = gr.Button("🧪 Start Quiz", visible=False)

    quiz_area = gr.Column(visible=False)
    question_display = gr.Textbox(label="Question", lines=4, interactive=False)
    answer_input = gr.Textbox(label="Your Answer (A/B/C/D)", lines=1)
    next_btn = gr.Button("Next")
    finish_msg = gr.Textbox(label="", lines=1, interactive=False)
    show_score_btn = gr.Button("Show Score")
    score_output = gr.Textbox(label="Results", lines=10, interactive=False)

    file_input.change(fn=upload_file, inputs=file_input, outputs=[summary_output, start_btn])
    start_btn.click(fn=start_quiz, outputs=question_display).then(lambda: gr.update(visible=True), outputs=quiz_area)
    next_btn.click(fn=submit_answer, inputs=answer_input, outputs=[question_display, finish_msg])
    show_score_btn.click(fn=show_score, outputs=score_output)

demo.launch()
