## Connecting the Dots Challenge – Round 1A: Document Structure Extraction

Welcome to our solution for Round 1A of the Adobe "Connecting the Dots" Challenge!

## Challenge Overview

- **Task:** Build an offline system to extract structured outlines (title, headings H1/H2/H3 with their text and page numbers) from PDF documents (≤50 pages).
- **Goal:** Generate a clean, hierarchical JSON capturing the structure of each PDF, enabling smarter document navigation and semantic search.
- **Key Requirements:**
    - Offline, CPU-only (amd64/x86_64) solution (no internet/network calls).
    - Model size ≤200MB (if any machine learning is used).
    - Fast: Processing time ≤10 seconds for a 50-page PDF.
    - Process all PDFs in `/app/input`, output corresponding JSONs in `/app/output`.


## Approach

Our solution consists of the following steps:

1. **PDF Parsing:**
    - Uses PyMuPDF/pdfminer/pdfplumber to extract text, bounding box info, and font properties.
    - For each page, scans lines/blocks for potential headings based on a combination of:
        - Font size/style/boldness
        - Position within the page
        - Regex patterns (e.g., numbering, capitalization)
        - Hierarchical cues (indentation, font difference, etc.)
2. **Title Detection:**
    - Heuristics to identify document title (often largest/first heading on first page).
3. **Outline Construction:**
    - For each detected heading:
        - Classifies into H1/H2/H3 using font and layout features.
        - Captures the page number, assigns the proper hierarchy.
    - Builds hierarchical structure (as flat or nested as appropriate) in the prescribed JSON format.
4. **Multilingual Support:**
    - Handles various scripts and language features (e.g., bonus for Japanese or non-Latin scripts).
5. **Performance:**
    - Optimized for <10sec total runtime for 50 pages.
    - Model (if used) is ≤200MB and runs on CPU.
    - Modular code for easy extension.

## File Structure

- `/app/input` — Directory where PDFs are placed for processing.
- `/app/output` — Directory where generated JSON outline files will be written.
- `main.py` — Entry point for processing.
- `Dockerfile` — Containerizes the solution as per requirements.
- `requirements.txt` — Python dependencies.

## How to Build \& Run

### Build the Docker Image

```bash
docker build --platform linux/amd64 -t mysolutionname:somerandomidentifier .
```


### Run the Container

```bash
docker run --rm \
    -v $(pwd)/input:/app/input \
    -v $(pwd)/output:/app/output \
    --network none \
    mysolutionname:somerandomidentifier
```

- Place all PDFs to be processed in the `/input` directory (max. 50 pages each).
- After running, corresponding JSON outline(s) will appear in `/output`.


### Notes

- **No GPU needed** — runs entirely on CPU, optimized for 8 CPUs and 16GB RAM.
- **No internet access required/allowed.**
- No hardcoded logic or file-specific hacks.
- Tested on both simple and complex PDFs, and for multilingual documents.


## Docker/Environment Notes

- Follows all requirements for AMD64 (`FROM --platform=linux/amd64 ...`).
- All dependencies installed inside the container.
- No external calls at runtime (fully offline).
- Model files (if any) are included within image \& meet size constraint.


## Libraries \& Models Used

- Main extraction: [insert main package used]
- (Optional) ML model for heading detection: [insert model file name and size, if any]
- JSON schema validation: [insert package]


## Additional Information

- If you wish to run locally:
    - Ensure Python 3.8+ and all dependencies (`pip install -r requirements.txt`) are available.
    - Run `python main.py /app/input /app/output`
- For questions, please refer to our `approach_explanation.md` in the repo.
