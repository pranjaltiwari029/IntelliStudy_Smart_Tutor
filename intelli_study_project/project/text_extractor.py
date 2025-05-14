import os
import pdfplumber
import docx2txt

def extract_text_from_pdf(file_path):
    text = ''
    print("[*] Opening PDF...")
    try:
        with pdfplumber.open(file_path) as pdf:
            if not pdf.pages:
                print("⚠️ No pages found in the PDF.")
                return ""
            for i, page in enumerate(pdf.pages):
                page_text = page.extract_text()
                if page_text:
                    print(f"✅ Extracted text from page {i+1}")
                    text += page_text + '\n'
                else:
                    print(f"⚠️ Page {i+1} has no readable text.")
        return text
    except Exception as e:
        print(f"❌ Error reading PDF: {e}")
        return ""

def extract_text_from_docx(file_path):
    print("[*] Extracting text from DOCX...")
    try:
        return docx2txt.process(file_path)
    except Exception as e:
        print(f"❌ Error reading DOCX: {e}")
        return ""

def extract_text(file_path):
    if file_path.lower().endswith('.pdf'):
        return extract_text_from_pdf(file_path)
    elif file_path.lower().endswith('.docx'):
        return extract_text_from_docx(file_path)
    else:
        raise ValueError("❌ Unsupported file type. Please use a PDF or DOCX file.")

if __name__ == "__main__":
    print("📚 IntelliStudy – Text Extractor Module")
    path = input("📂 Enter full path to PDF or DOCX file: ").strip()

    if not os.path.isfile(path):
        print("❌ File not found. Please check the path and try again.")
    else:
        print(f"📄 Reading file: {os.path.basename(path)}")
        text = extract_text(path)

        if text.strip():
            print("\n✅ --- Extracted Text Preview ---\n")
            print(text[:1000] + '\n... [Text truncated]' if len(text) > 1000 else text)

            output_file = "extracted_output.txt"
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(text)
            print(f"\n💾 Text saved to: {output_file}")
        else:
            print("⚠️ No text could be extracted. The file may contain scanned images or be empty.")
