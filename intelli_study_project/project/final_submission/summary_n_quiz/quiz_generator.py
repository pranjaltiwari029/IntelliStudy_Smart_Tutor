import requests

GROQ_ENDPOINT = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama3-70b-8192"

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

def generate_mcq_questions_individually(document_text):
    questions = []
    for i in range(1, 6):
        previous_questions = "\n".join(questions)
        prompt = (
            f"You are generating a quiz. Please generate one unique and non-repetitive multiple choice question labeled as Q{i} "
            "based on the following study material. Ensure the question is different from earlier ones. "
            "Include 4 answer options labeled A) to D). Begin the question with 'Q{i}:' and do not include the correct answer."
            f"\n\nStudy Material:\n{document_text}\n\n"
            f"Previous Questions:\n{previous_questions}"
        )
        question = groq_chat([{ "role": "user", "content": prompt }])
        questions.append(question)
    return questions


def generate_answer_key(document_text, questions):
    prompt = (
        "You are an AI assistant. Based on the study material below, provide the correct answer for each multiple choice question.\n"
        "For each question:\n"
        "- Show only the question text and the correct answer.\n"
        "- List the correct answer option (A, B, C, or D) followed by the full text of that option.\n\n"
        "Format:\n"
        "Q1: [Question text]\nCorrect Answer: C) [Full answer text]\n\n"
        "Do not include incorrect options or explanations.\n\n"
        f"Study Material:\n{document_text}\n\n"
        "Questions:\n" + "\n\n".join(questions)
    )
    return groq_chat([{ "role": "user", "content": prompt }])

def run_interactive_quiz(document_text):
    print("\nGenerating quiz questions...")
    questions = generate_mcq_questions_individually(document_text)
    user_answers = []

    for i, question in enumerate(questions, start=1):
        print(f"\n{question}")
        answer = ""
        while answer not in ["A", "B", "C", "D"]:
            answer = input("Your answer (A/B/C/D): ").strip().upper()
        user_answers.append(answer)

    print("\nGenerating correct answers...")
    correct_answers = generate_answer_key(document_text, questions)
    print("\nCorrect Answers:\n")
    print(correct_answers)
