import os
import pdfplumber
from docx import Document
import requests
import re

# GROQ API configuration
GROQ_ENDPOINT = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama3-70b-8192"

def extract_text_from_pdf(file_path):
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text

def extract_text_from_docx(file_path):
    doc = Document(file_path)
    return "\n".join([para.text for para in doc.paragraphs if para.text.strip()])

def extract_text(file_path):
    if file_path.lower().endswith(".pdf"):
        return extract_text_from_pdf(file_path)
    elif file_path.lower().endswith(".docx"):
        return extract_text_from_docx(file_path)
    else:
        raise ValueError("Unsupported file type. Use PDF or DOCX.")

def detect_sections(text):
    heading_pattern = re.compile(r"^([A-Z][A-Za-z0-9\s\-:,.]{3,})$", re.MULTILINE)
    matches = list(heading_pattern.finditer(text))
    sections = {}
    for i, match in enumerate(matches):
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        heading = match.group().strip()
        content = text[start:end].strip()
        sections[heading] = content
    return sections

def groq_chat(messages):
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": GROQ_MODEL,
        "messages": messages,
        "temperature": 0.7
    }
    try:
        response = requests.post(GROQ_ENDPOINT, headers=headers, json=data)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content'].strip()
    except Exception as e:
        return f"[Error: {e}]"

def summarize_section(text):
    messages = [
        {
            "role": "user",
            "content": f"Summarize the following content in a concise and clear way for study purposes:\n\n{text}"
        }
    ]
    return groq_chat(messages)

# def generate_quiz(title, text):
#     messages = [
#         {
#             "role": "user",
#             "content": (
#                 f"Generate exactly 2 study quiz questions based on the following topic titled '{title}'. "
#                 "They should be a mix of multiple-choice and short-answer. Number the questions clearly (1 and 2):\n\n"
#                 f"{text}"
#             )
#         }
#     ]
#     return groq_chat(messages)
def generate_quiz(title, text):
    messages = [
        {
            "role": "user",
            "content": (
                f"Generate exactly 2 study quiz questions based on the topic '{title}'. "
                "One question should be multiple choice (labeled A–D), and the second should be short answer. "
                "Do NOT include the correct answers or any explanations. Only return the questions like this:\n\n"
                "1. What is the primary source of carbon dioxide in the atmosphere?\n"
                "A) Option A\nB) Option B\nC) Option C\nD) Option D\n\n"
                "2. What is a secondary greenhouse gas besides carbon dioxide?"
            )
        }
    ]
    return groq_chat(messages)

def generate_answer_key(title, questions, text):
    messages = [
        {
            "role": "user",
            "content": (
                f"Based on the content titled '{title}', provide correct answers to the following quiz questions. "
                f"Answer clearly for each question numbered 1 and 2:\n\n{text}\n\nQuestions:\n{questions}"
            )
        }
    ]
    return groq_chat(messages)

def generate_flashcards(title, text):
    messages = [
        {
            "role": "user",
            "content": (
                f"Create 3 flashcards based on the topic '{title}'. "
                "Format each as:\nQ: question\nA: answer\n\nOnly return 3 cards:\n\n"
                f"{text}"
            )
        }
    ]
    return groq_chat(messages)

def prompt_user_answers(quiz_text):
    print("📝 Please answer the following questions:\n")
    user_answers = ""
    answers_list = []

    # Split questions based on line numbers or identifiers
    question_blocks = quiz_text.strip().split('\n\n')
    for block in question_blocks:
        lines = block.strip().split('\n')
        question = "\n".join(lines)
        print(question)
        ans = input("Your answer: ")
        user_answers += f"{question}\nYour answer: {ans}\n"
        answers_list.append(ans.strip().lower())

    return user_answers, answers_list, question_blocks

def check_score(user_answers, correct_answers):
    score = 0
    total = min(len(user_answers), len(correct_answers))
    feedback = ""
    for i in range(total):
        correct = correct_answers[i].strip().lower()
        user = user_answers[i]
        match = correct in user or user in correct  # Loose match
        feedback += f"\nQ{i+1}: {'✅ Correct' if match else '❌ Incorrect'} (Your: {user} | Answer: {correct})"
        if match:
            score += 1
    return score, total, feedback


if __name__ == "__main__":
    print("📘 IntelliStudy – Groq + LLaMA 3 | Summarizer + Quiz + Flashcards")
    path = input("Enter full path to your PDF or DOCX file: ").strip()

    if not os.path.isfile(path):
        print("❌ File not found.")
        exit()

    raw_text = extract_text(path)
    sections = detect_sections(raw_text)

    full_output = ""
    for heading, body in sections.items():
        print(f"\n🧠 Summarizing section: {heading}")
        summary = summarize_section(body)
        print(f"✅ Summary:\n{summary}\n")
        full_output += f"\n{heading}\nSummary:\n{summary}\n"

        print(f"🧪 Generating quiz for: {heading}")
        quiz = generate_quiz(heading, body)
        print(f"📚 Quiz:\n{quiz}\n")
        full_output += f"Quiz:\n{quiz}\n"

        user_responses, user_answer_list, question_list = prompt_user_answers(quiz)
        full_output += f"User Answers:\n{user_responses}\n"

        print("🎯 Checking answers...")
        answer_key_text = generate_answer_key(heading, quiz, body)
        correct_answers = [line for line in answer_key_text.split('\n') if line.strip()]
        score, total, feedback = check_score(user_answer_list, correct_answers)

        print(f"✅ Score for '{heading}': {score}/{total}")
        print(feedback)

        full_output += f"Answer Key:\n{answer_key_text}\n"
        full_output += f"Score: {score}/{total}\n{feedback}\n"

        print(f"🃏 Generating flashcards for: {heading}")
        flashcards = generate_flashcards(heading, body)
        print(f"🃏 Flashcards:\n{flashcards}\n")
        full_output += f"Flashcards:\n{flashcards}\n"

    save = input("💾 Save everything to file? (y/n): ").strip().lower()
    if save == 'y':
        with open("llama_groq_summary_output.txt", "w", encoding="utf-8") as f:
            f.write(full_output)
        print("✅ Output saved to llama_groq_summary_output.txt")
