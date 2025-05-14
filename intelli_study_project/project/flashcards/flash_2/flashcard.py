import re
import requests

GROQ_ENDPOINT = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama3-70b-8192"

def call_groq_qa_generation(text):
    prompt = (
        "You are an expert flashcard generator. Given a code snippet or technical concept, extract up to 5 advanced programming-related flashcards.\n"
        "Each flashcard must include:\n"
        "1. A meaningful question that tests understanding (not just recall).\n"
        "2. A helpful answer (can include explanations or code).\n"
        "3. A difficulty level (Easy, Medium, Hard).\n\n"
        "Output format:\n"
        "Question: <...>\n"
        "Answer: <...>\n"
        "Difficulty: <Easy|Medium|Hard>\n"
        "---\n"
        f"\nInput:\n{text}"
    )

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": GROQ_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.5
    }

    response = requests.post(GROQ_ENDPOINT, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()['choices'][0]['message']['content']

def parse_flashcards(raw_text):
    flashcards = []
    blocks = raw_text.strip().split("---")
    for block in blocks:
        q_match = re.search(r"Question:\s*(.+?)\n", block, re.DOTALL)
        a_match = re.search(r"Answer:\s*(.+?)\n", block, re.DOTALL)
        d_match = re.search(r"Difficulty:\s*(\w+)", block)
        if q_match and a_match and d_match:
            flashcards.append({
                "question": q_match.group(1).strip(),
                "answer": a_match.group(1).strip(),
                "difficulty": d_match.group(1).capitalize()
            })
    return flashcards

def generate_flashcards(text):
    try:
        raw_output = call_groq_qa_generation(text)
        return parse_flashcards(raw_output)
    except Exception as e:
        return [{
            "question": "Error generating flashcards.",
            "answer": str(e),
            "difficulty": "N/A"
        }]
