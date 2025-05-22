import os
import pdfplumber
from docx import Document
import re
import requests

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

def summarize_sections(sections):
    summaries = {}
    for heading, content in sections.items():
        print(f"\n🧠 Summarizing: {heading}")
        summary = groq_chat([
            {
                "role": "user",
                "content": f"Summarize the following content for study purposes:\n\n{content}"
            }
        ])
        print(f"✅ Summary: {summary}\n")
        summaries[heading] = summary
    return summaries
