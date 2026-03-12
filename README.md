# VextaAI - Personal Research Assistant

A document-based research assistant that lets you upload PDF documents and have AI-powered conversations with them. Built with Claude, PageIndex, and Streamlit.

---

## What It Does

- Upload PDF documents through a web interface
- Automatically ingests and indexes documents using the PageIndex API
- Ask natural language questions about your documents
- Get accurate, context-aware answers powered by Claude
- Tracks ingestion history to avoid re-uploading the same files

---

## Tech Stack

| Component | Technology |
|-----------|------------|
| Frontend | [Streamlit](https://streamlit.io/) |
| AI Model | [Claude](https://www.anthropic.com/claude) (via PageIndex) |
| Document Storage & Retrieval | [PageIndex](https://pageindex.ai/) |
| MCP Integration | [PageIndex MCP](https://docs.pageindex.ai/) |
| PDF Processing | PyPDF2, ReportLab |
| Language | Python 3.10+ |

---

## Project Structure

```
personal-research-assistant/
├── src/
│   ├── app.py          # Streamlit web app (main UI)
│   ├── chat.py         # PageIndex chat API integration
│   └── ingest.py       # Document ingestion pipeline
├── docs/               # Drop PDF files here for batch ingestion
├── ingest_log.json     # Tracks which files have been ingested
├── .env                # API keys (not committed)
└── README.md
```

---

## Setup

### 1. Clone the repository

```bash
git clone <repo-url>
cd personal-research-assistant
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install streamlit requests python-dotenv PyPDF2 reportlab
```

### 4. Configure environment variables

Create a `.env` file in the project root:

```env
PAGEINDEX_API_KEY=your_pageindex_api_key_here
```

Get your API key from [pageindex.ai](https://pageindex.ai/).

---

## Running the App

### Web Interface (Streamlit)

```bash
streamlit run src/app.py
```

Open `http://localhost:8501` in your browser. Use the sidebar to upload PDFs and select a document, then chat with it in the main panel.

### Batch Ingestion (CLI)

Place PDF, TXT, or Markdown files in the `docs/` folder, then run:

```bash
python src/ingest.py
```

Already-ingested files are tracked in `ingest_log.json` and skipped on subsequent runs.

### CLI Chat

```bash
python src/chat.py
```

Select a document by number and ask questions interactively.

---

## Usage

1. **Upload** a PDF via the Streamlit sidebar or place files in `docs/` and run `ingest.py`
2. **Select** a document from the dropdown in the sidebar
3. **Ask** questions in the chat input — the assistant answers based on the document content
