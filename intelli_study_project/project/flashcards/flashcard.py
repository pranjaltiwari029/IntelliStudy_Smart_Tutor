# flashcard_generator.py

def generate_flashcards_from_text(text):
    """
    Very basic Q&A generation from text chunks.
    """
    lines = text.strip().split('\n')
    flashcards = []
    for line in lines:
        if ':' in line:
            question, answer = line.split(':', 1)
            flashcards.append({"question": question.strip(), "answer": answer.strip()})
    return flashcards
