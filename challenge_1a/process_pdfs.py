import os
import json
from PyPDF2 import PdfReader

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_DIR = os.path.join(BASE_DIR, "input")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")

def extract_outline(pdf_path):
    try:
        reader = PdfReader(pdf_path)

        # Use 'outline' instead of deprecated 'outlines'
        outlines = getattr(reader, "outline", None)
        if not outlines:
            print(f"No outline found in {pdf_path}")
            return

        def parse_outline(items, level=1):
            outline_list = []
            for item in items:
                if isinstance(item, list):
                    outline_list.extend(parse_outline(item, level + 1))
                else:
                    try:
                        page_num = reader.get_destination_page_number(item) + 1
                        outline_list.append({
                            "level": f"H{min(level, 3)}",
                            "text": item.title,
                            "page": page_num
                        })
                    except Exception:
                        continue
            return outline_list

        parsed_outline = parse_outline(outlines)

        output_data = {
            "title": os.path.splitext(os.path.basename(pdf_path))[0],
            "outline": parsed_outline
        }

        if not os.path.exists(OUTPUT_DIR):
            os.makedirs(OUTPUT_DIR)

        output_file = os.path.join(
            OUTPUT_DIR,
            os.path.basename(pdf_path).replace(".pdf", ".json")
        )

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)

        print(f"JSON saved: {output_file}")

    except Exception as e:
        print(f"Failed to extract outline from {pdf_path}: {e}")

def main():
    if not os.path.exists(INPUT_DIR):
        print(f"Input folder not found: {INPUT_DIR}")
        return

    pdf_files = [
        f for f in os.listdir(INPUT_DIR)
        if f.lower().endswith(".pdf") and not f.startswith("~$")
    ]
    if not pdf_files:
        print("No PDF files found in input folder.")
        return

    print(f"Found {len(pdf_files)} PDF(s) in input folder.\n")

    for filename in pdf_files:
        pdf_path = os.path.join(INPUT_DIR, filename)
        print(f"Processing: {pdf_path}")
        extract_outline(pdf_path)

if __name__ == "__main__":
    main()
