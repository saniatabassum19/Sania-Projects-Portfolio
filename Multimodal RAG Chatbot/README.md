# Multimodal RAG Chatbot

A document question-answering application that uses retrieval-augmented generation
(RAG) to answer questions from PDFs, images, CSV files, and Excel workbooks. The app
retrieves relevant content with FAISS and generates grounded answers with Google
Gemini, including source filenames and page numbers when available.

## Features

- Upload one or more supported documents through a Streamlit interface
- Extract text from PDFs with PyMuPDF
- Extract text from PNG and JPEG images with EasyOCR
- Read structured data from CSV and Excel files with pandas
- Split long documents into overlapping chunks with LangChain
- Create local embeddings with `all-MiniLM-L6-v2`
- Retrieve relevant chunks using FAISS similarity search
- Generate context-grounded answers with Gemini 2.5 Flash
- Display the source files and PDF page numbers used for retrieval

## Tech Stack

- Python
- Streamlit
- LangChain
- Google Gemini API
- Hugging Face Sentence Transformers
- FAISS
- PyMuPDF
- EasyOCR
- pandas

## How It Works

```text
Uploaded document
       |
       v
Text extraction / OCR
       |
       v
Overlapping text chunks
       |
       v
Sentence-transformer embeddings
       |
       v
FAISS vector store
       |
       v
Relevant chunks + user question
       |
       v
Gemini answer with sources
```

## Project Structure

```text
.
|-- app.py                 # Streamlit user interface
|-- src/
|   |-- loader.py          # PDF, image, CSV, and Excel extraction
|   |-- chunker.py         # Document chunking
|   |-- embeddings.py      # Sentence-transformer embeddings
|   |-- vectorstore.py     # FAISS vector store management
|   |-- retriever.py       # Similarity-based retrieval
|   `-- llm.py             # Gemini prompting and answer generation
|-- data/pdfs/sample.pdf   # Sample document for pipeline testing
|-- test_llm.py            # Gemini connection check
|-- test_pipeline.py       # End-to-end pipeline check
|-- requirements.txt
`-- .env.example
```

## Setup

### 1. Create a virtual environment

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

On macOS or Linux, activate it with:

```bash
source .venv/bin/activate
```

### 2. Install dependencies

```powershell
python -m pip install -r requirements.txt
```

The first embedding or OCR run may take longer while model files are downloaded.

### 3. Configure Gemini

Create a `.env` file in the project root using `.env.example` as a template:

```env
GOOGLE_API_KEY=your_google_api_key_here
```

Do not commit `.env` or expose your API key publicly.

## Run the Application

```powershell
python -m streamlit run app.py
```

Open the local URL shown in the terminal, upload a document, wait for indexing to
finish, and enter a question in the chat box.

## Verify the Project

Test the Gemini connection:

```powershell
python test_llm.py
```

Run the complete pipeline against `data/pdfs/sample.pdf`:

```powershell
python test_pipeline.py
```

## Supported Files

| Format | Extension | Processing method |
|---|---|---|
| PDF | `.pdf` | PyMuPDF text extraction |
| Image | `.png`, `.jpg`, `.jpeg` | EasyOCR |
| CSV | `.csv` | pandas |
| Excel | `.xlsx` | pandas and OpenPyXL |

## Current Limitations

- The application rebuilds its in-memory vector store when uploaded files change.
- Retrieved sources indicate relevant chunks, not sentence-level citations.
- OCR and embedding models can require significant memory and startup time.
- Chat history is displayed but is not currently included in retrieval or prompts.

## Future Improvements

- Add automated unit and retrieval-quality tests
- Cache OCR and embedding models between Streamlit reruns
- Add persistent vector indexes for previously processed documents
- Improve citation precision and relevance scoring
- Add conversational follow-up support
- Add authentication, rate limiting, and deployment configuration
