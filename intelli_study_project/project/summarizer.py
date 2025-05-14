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

def generate_mcq_quiz(text):
    messages = [
        {
            "role": "user",
            "content": (
                "Generate exactly 5 multiple choice questions based on the following text. "
                "Each question should have four options (A-D). Format:\n"
                "1. Question?\nA) ...\nB) ...\nC) ...\nD) ...\n"
                "Only include the questions and options, not the answers.\n\n"
                f"{text}"
            )
        }
    ]
    return groq_chat(messages)

def generate_answer_key_for_mcq(text, quiz_text):
    messages = [
        {
            "role": "user",
            "content": (
                "Here is the quiz based on the text. Provide the correct option (A, B, C, or D) for each question only. "
                "Format: 1. A\n2. C ...\n\n"
                f"Text:\n{text}\n\nQuiz:\n{quiz_text}"
            )
        }
    ]
    return groq_chat(messages)

def get_user_mcq_answers(quiz_text):
    print("📝 Please answer the following questions by entering A, B, C, or D:\n")
    user_answers = []
    question_blocks = re.findall(r"(\d+\..*?(?:\nA\).*?\nB\).*?\nC\).*?\nD\).*?))(?=\n\d+\.|\Z)", quiz_text, re.DOTALL)

    for block in question_blocks:
        print(block.strip())
        while True:
            ans = input("Your answer (A/B/C/D): ").strip().upper()
            if ans in ["A", "B", "C", "D"]:
                break
            else:
                print("Invalid input. Please enter A, B, C, or D.")
        user_answers.append(ans)
    return user_answers

def score_mcq(user_answers, correct_keys):
    correct_lines = re.findall(r"\d+\.\s*([A-D])", correct_keys)
    score = 0
    feedback = ""
    for i, (u, c) in enumerate(zip(user_answers, correct_lines)):
        result = "✅ Correct" if u == c else "❌ Incorrect"
        feedback += f"Q{i+1}: {result} (Your: {u} | Correct: {c})\n"
        if u == c:
            score += 1
    return score, len(correct_lines), feedback

if __name__ == "__main__":
    print("📘 IntelliStudy – Groq + LLaMA 3 | Summarizer + MCQ Quiz")
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

    print("🧪 Generating 5-question MCQ quiz based on entire document...")
    mcq_quiz = generate_mcq_quiz(raw_text)
    print(f"📚 Quiz:\n{mcq_quiz}\n")
    full_output += f"\n5 MCQ Quiz:\n{mcq_quiz}\n"

    user_mcq_answers = get_user_mcq_answers(mcq_quiz)

    print("🎯 Generating answer key...")
    answer_key = generate_answer_key_for_mcq(raw_text, mcq_quiz)
    print(f"🗝️ Answer Key:\n{answer_key}\n")

    score, total, feedback = score_mcq(user_mcq_answers, answer_key)
    print(f"🎉 Final Score: {score}/{total}")
    print(feedback)

    full_output += f"Answer Key:\n{answer_key}\nScore: {score}/{total}\n{feedback}\n"

    save = input("💾 Save everything to file? (y/n): ").strip().lower()
    if save == 'y':
        with open("llama_groq_summary_output.txt", "w", encoding="utf-8") as f:
            f.write(full_output)
        print("✅ Output saved to llama_groq_summary_output.txt")
