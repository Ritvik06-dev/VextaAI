import os
import json
import requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

PAGEINDEX_API_KEY = os.getenv("PAGEINDEX_API_KEY")

#BASE URL for PageIndex API
PAGEINDEX_BASE_URL = "https://api.pageindex.ai"

#PATH TO THE LOG FILE THAT TRACKS WHATS ALREADY BEEN INGESTED
LOG_FILE = Path("ingest_log.json")

DOCS_FOLDER = Path(__file__).parent.parent / "docs"

def load_log():#if the log file exists, load it, otherwise return an empty dict
    if LOG_FILE.exists():
        with open(LOG_FILE, "r") as f:
            return json.load(f)
    return {}

def save_log(log): #save the log to the log file
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "w") as f:
        json.dump(log, f, indent=2)

def extract_text(file_path):#Get the file extension to determine how to read it
    ext = file_path.suffix.lower()

    if ext == ".txt":
        for encoding in ("utf-8", "utf-16", "latin-1"):
            try:
                with open(file_path, "r", encoding=encoding) as f:
                    return f.read()
            except UnicodeDecodeError:
                continue
        print(f"Could not decode {file_path.name} with any supported encoding.")
        return None
        
    elif ext == ".md":
        for encoding in ("utf-8", "utf-16", "latin-1"):
            try:
                with open(file_path, "r", encoding=encoding) as f:
                    return f.read()
            except UnicodeDecodeError:
                continue
        print(f"Could not decode {file_path.name} with any supported encoding.")
        return None
        
    elif ext == ".pdf":
        import PyPDF2
        text = ""
        with open(file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text += page.extract_text()
        return text

    else:
        print(f"Unsupported file type: {ext}")
        return None
    
def send_to_pageindex(filename, text):
    from reportlab.lib.pagesizes import LETTER
    from reportlab.pdfgen import canvas
    import tempfile

    # write text to a temporary PDF
    tmp_path = Path(tempfile.mktemp(suffix=".pdf"))
    c = canvas.Canvas(str(tmp_path), pagesize=LETTER)
    width, height = LETTER
    margin, line_height = 50, 14
    y = height - margin
    for line in text.splitlines():
        if y < margin:
            c.showPage()
            y = height - margin
        c.drawString(margin, y, line)
        y -= line_height
    c.save()

    pdf_filename = Path(filename).stem + ".pdf"
    headers = {"api_key": PAGEINDEX_API_KEY}
    try:
        with open(tmp_path, "rb") as f:
            files = {"file": (pdf_filename, f, "application/pdf")}
            response = requests.post(f"{PAGEINDEX_BASE_URL}/doc/", headers=headers, files=files)
    finally:
        tmp_path.unlink(missing_ok=True)

    #check if the request was successful
    if response.status_code == 200 or response.status_code == 201:
        print(f"Successfully ingested {filename}")
        return True
    else:
        print(f"Failed to ingest {filename}: {response.status_code} - {response.text}")
        return False
#main function to process the documents in the docs folder
def ingest_docs():
    #debug: show resolved path and files found
    print(f"Looking for docs in: {DOCS_FOLDER.resolve()}")
    if DOCS_FOLDER.exists():
        files = list(DOCS_FOLDER.iterdir())
        print(f"Found {len(files)} items: {[f.name for f in files]}")
    else:
        print("ERROR: docs folder does not exist at that path!")
        return

    #load the log to see which files have already been ingested
    log = load_log()

    #iterate through all files in the docs folder
    for file_path in DOCS_FOLDER.iterdir():
        #skip if its a folder, not a file
        if not file_path.is_file():
            continue

        #skip if we have already ingested this file
        if file_path.name in log:
            print(f"Skipping {file_path.name}, already ingested.")
            continue

        #extract text from the file
        print(f"Extracting text from {file_path.name}...")

        text = extract_text(file_path)

        #skip if we couldn't extract text
        if text is None:
            continue

        #send the extracted text to the PageIndex API
        success = send_to_pageindex(file_path.name, text)

        #if the ingestion was successful, update the log
        if success:
            log[file_path.name] = {
                "status": "ingested",
                "path": str(file_path)
            }
            save_log(log)

#run the main function when the script is executed
if __name__ == "__main__":
    print("Starting ingestion process...")
    ingest_docs()
    print("Ingestion process completed.")