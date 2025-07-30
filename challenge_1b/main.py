import os
import json
import unicodedata
from datetime import datetime
from langdetect import detect, DetectorFactory
from PyPDF2 import PdfReader
from sentence_transformers import SentenceTransformer, util

DetectorFactory.seed = 0

# === Paths ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_DIR = os.path.join(BASE_DIR, "input")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
PERSONA_FILE = os.path.join(INPUT_DIR, "persona.json")

# === Model (<=1GB) ===
MODEL = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

def load_persona_data():
    if not os.path.exists(PERSONA_FILE):
        return {}, "", []
    with open(PERSONA_FILE, "r", encoding="utf-8") as f:
        persona = json.load(f)
        combined_text = ""
        keywords = []
        if "role" in persona:
            combined_text += persona["role"] + " "
            keywords += persona["role"].lower().split()
        if "goal" in persona:
            combined_text += persona["goal"]
            keywords += persona["goal"].lower().split()
        return persona, combined_text.strip(), list(set(keywords))

def calculate_similarity(section_text, persona_task_embedding):
    section_embedding = MODEL.encode(section_text, convert_to_tensor=True)
    score = util.cos_sim(persona_task_embedding, section_embedding).item()
    return round(score, 4)

def extract_outline_or_text(pdf_path, persona_embedding):
    reader = PdfReader(pdf_path)
    results = []

    try:
        outlines = reader.outline
    except:
        outlines = []

    # If outline exists, parse it
    if outlines:
        def parse_outline(items, level=1):
            section_results = []
            for item in items:
                if isinstance(item, list):
                    section_results.extend(parse_outline(item, level + 1))
                else:
                    try:
                        title = unicodedata.normalize("NFKC", item.title).strip()
                        if len(title) < 2:
                            continue
                        page_num = reader.get_destination_page_number(item) + 1
                        language = detect(title) if len(title.strip()) > 2 else "unknown"
                        importance = calculate_similarity(title, persona_embedding)

                        section_results.append({
                            "document": os.path.basename(pdf_path),
                            "page_number": page_num,
                            "section_title": title,
                            "importance_rank": importance,
                            "language": language,
                            "level": f"H{min(level, 3)}"
                        })
                    except:
                        continue
            return section_results

        results = parse_outline(outlines)

    # Fallback: No outlines, extract from text content
    if not results:
        for i, page in enumerate(reader.pages):
            text = page.extract_text()
            if not text:
                continue
            lines = [line.strip() for line in text.split("\n") if len(line.strip()) > 5]
            for line in lines[:5]:  # take top few lines as potential section headings
                try:
                    language = detect(line)
                except:
                    language = "unknown"
                importance = calculate_similarity(line, persona_embedding)
                results.append({
                    "document": os.path.basename(pdf_path),
                    "page_number": i + 1,
                    "section_title": line,
                    "importance_rank": importance,
                    "language": language,
                    "level": "H2"
                })
    return results

def main():
    if not os.path.exists(INPUT_DIR):
        print("❌ Input folder not found.")
        return

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    pdf_files = [f for f in os.listdir(INPUT_DIR) if f.lower().endswith(".pdf")]
    if not pdf_files:
        print("⚠️ No PDFs found in input folder.")
        return

    # === Load persona data ===
    persona, persona_text, persona_keywords = load_persona_data()
    persona_embedding = MODEL.encode(persona_text, convert_to_tensor=True)
    timestamp = datetime.now().isoformat()

    metadata = {
        "input_documents": pdf_files,
        "persona": persona.get("role", "N/A"),
        "job_to_be_done": persona.get("goal", "N/A"),
        "processing_timestamp": timestamp
    }

    extracted_sections = []

    for file in pdf_files:
        path = os.path.join(INPUT_DIR, file)
        sections = extract_outline_or_text(path, persona_embedding)
        sections = sorted(sections, key=lambda x: x["importance_rank"], reverse=True)
        extracted_sections.extend(sections)

    output = {
        "metadata": metadata,
        "extracted_sections": extracted_sections,
        "subsection_analysis": []  # Placeholder for future extension
    }

    output_path = os.path.join(OUTPUT_DIR, "round1b_output.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"✅ Final output saved at: {output_path}")

if __name__ == "__main__":
    main()
