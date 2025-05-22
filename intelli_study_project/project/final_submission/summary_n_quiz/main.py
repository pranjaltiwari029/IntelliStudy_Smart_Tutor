from summarizer import extract_text, detect_sections, summarize_sections
from quiz_generator import generate_mcq_questions_individually, generate_answer_key
import os

if __name__ == "__main__":
    print("📘 IntelliStudy – Summarizer + Quiz Generator")
    path = input("Enter the full path to your PDF or DOCX file: ").strip()

    if not os.path.isfile(path):
        print("❌ File not found.")
        exit()

    raw_text = extract_text(path)
    sections = detect_sections(raw_text)
    summaries = summarize_sections(sections)

    print("🧪 Generating MCQ quiz based on the full document...")
    quiz = generate_mcq_questions_individually(raw_text)
    print(f"📚 Quiz:\n{quiz}\n")

    user_answers = []
    print("📝 Answer the following questions by typing the letter (A/B/C/D):\n")
    
    for i, question in enumerate(quiz, start=1):
        print(f"\nQuestion {i}:")
        print(question)
        answer = input("Your answer (A/B/C/D): ").strip().upper()
        user_answers.append(answer)

    print("🎯 Generating answer key...")
    answer_key = generate_answer_key(raw_text, quiz)
    print(f"Answer Key:\n{answer_key}\n")

    correct_lines = [line for line in answer_key.split('\n') if line.strip() and any(opt in line for opt in ['A', 'B', 'C', 'D'])]

    score = 0
    feedback = ""
    for i in range(min(len(user_answers), len(correct_lines))):
        correct = correct_lines[i].split()[-1].strip(".)")
        user = user_answers[i]
        is_correct = user == correct.upper()
        feedback += f"Q{i+1}: {'✅' if is_correct else '❌'} Your: {user} | Correct: {correct}\n"
        if is_correct:
            score += 1

    print(f"\n✅ Final Score: {score}/{len(correct_lines)}")
    print(feedback)
