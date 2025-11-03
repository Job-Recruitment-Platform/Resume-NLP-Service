from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from app.model_loader import (
    ner_pipeline,
    extract_skills_from_text,
    extract_email,
    extract_phone,
    extract_education_degree
)
from typing import Optional
import logging
import PyPDF2
import docx
import io
import re

app = FastAPI(title="CV Reader Service", version="1.0")

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def clean_text(text: str) -> str:
    """Clean extracted text for better NER results"""
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract text from PDF file"""
    try:
        pdf_file = io.BytesIO(file_bytes)
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text.strip()
    except Exception as e:
        logger.error(f"Error extracting PDF: {e}")
        raise HTTPException(
            status_code=400, detail="Could not extract text from PDF")


def extract_text_from_docx(file_bytes: bytes) -> str:
    """Extract text from DOCX file"""
    try:
        docx_file = io.BytesIO(file_bytes)
        doc = docx.Document(docx_file)
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        return text.strip()
    except Exception as e:
        logger.error(f"Error extracting DOCX: {e}")
        raise HTTPException(
            status_code=400, detail="Could not extract text from DOCX")


def post_process_entities(results: list, full_text: str) -> dict:
    """
    Extract all entities from CV using NER + custom extraction.
    Works for ANY industry and ANY location worldwide.
    """
    grouped_entities = {}

    # Process NER results
    for r in results:
        entity_type = r.get("entity_group", "").strip()
        value = r.get("word", "").strip()

        # Skip tokens starting with ## (subword tokens)
        if value.startswith("##"):
            continue

        # Skip very short or invalid values
        if len(value) < 2:
            continue

        if entity_type and value:
            # Map NER labels to readable names
            label_mapping = {
                "PER": "Name",
                "ORG": "Organization",
                "LOC": "Location",
                "MISC": "Other"
            }

            readable_label = label_mapping.get(entity_type, entity_type)

            if readable_label not in grouped_entities:
                grouped_entities[readable_label] = []

            # Avoid duplicates
            if value not in grouped_entities[readable_label]:
                grouped_entities[readable_label].append(value)

    # Extract Skills (section-based, works for any industry)
    skills = extract_skills_from_text(full_text)
    if skills:
        grouped_entities["Skills"] = skills

    # Extract Email
    emails = extract_email(full_text)
    if emails:
        grouped_entities["Email"] = emails

    # Extract Phone
    phones = extract_phone(full_text)
    if phones:
        grouped_entities["Phone"] = phones

    # Extract Education/Degree
    degrees = extract_education_degree(full_text)
    if degrees:
        grouped_entities["Education"] = degrees

    return grouped_entities


@app.get("/")
def root():
    return {"message": "Resume NER service is running!"}


@app.post("/extract")
async def extract_entities(
    file: Optional[UploadFile] = File(None),
    text: Optional[str] = Form(None)
):
    """
    API extract informations from CV (NER).
    Works for ANY industry and ANY location worldwide.
    Allowed:
      - file (pdf/txt/docx)
      - plaintext
    """
    if not file and not text:
        raise HTTPException(
            status_code=400, detail="You must send either file or text!")

    try:
        # --- Read content ---
        if file:
            filename = file.filename.lower()

            # Check valid file type
            if not any(filename.endswith(ext) for ext in [".txt", ".pdf", ".docx"]):
                raise HTTPException(
                    status_code=400,
                    detail="Only .txt, .pdf, or .docx formats are supported"
                )

            content_bytes = await file.read()

            # Extract text based on file type
            if filename.endswith(".pdf"):
                content = extract_text_from_pdf(content_bytes)
            elif filename.endswith(".docx"):
                content = extract_text_from_docx(content_bytes)
            else:  # .txt
                try:
                    content = content_bytes.decode("utf-8")
                except UnicodeDecodeError:
                    content = content_bytes.decode("latin-1", errors="ignore")

        else:
            # If sending text directly
            content = text.strip()
            if not content:
                raise HTTPException(
                    status_code=400, detail="Text cannot be empty!")

        # Check if content is empty after extraction
        if not content or len(content.strip()) == 0:
            raise HTTPException(
                status_code=400,
                detail="Could not extract any text from the file"
            )

        # Store original text for section-based extraction
        original_text = content

        # Clean the text for NER
        content = clean_text(content)

        # Minimum text length check
        if len(content) < 10:
            raise HTTPException(
                status_code=400,
                detail="Text is too short for entity extraction (minimum 10 characters)"
            )

        logger.info(f"Extracted text length: {len(content)} characters")

        # --- Call NER model ---
        logger.info("Running NER pipeline...")

        # Split long text into chunks (BERT has 512 token limit)
        max_length = 400
        chunks = [content[i:i+max_length]
                  for i in range(0, len(content), max_length)]

        all_results = []
        for i, chunk in enumerate(chunks):
            try:
                logger.info(f"Processing chunk {i+1}/{len(chunks)}")
                results = ner_pipeline(chunk)
                all_results.extend(results)
            except Exception as e:
                logger.error(f"Error processing chunk {i+1}: {e}")
                # Continue with other chunks
                continue

        logger.info(f"NER raw results count: {len(all_results)}")

        # --- Post-process and group entities ---
        grouped_entities = post_process_entities(all_results, original_text)

        logger.info(f"Grouped entities: {grouped_entities}")

        # --- Return ---
        return JSONResponse(
            status_code=200,
            content={
                "message": "Entity extraction successful",
                "entities": grouped_entities,
                "text_length": len(content),
                "chunks_processed": len(chunks)
            }
        )

    except HTTPException as e:
        raise e

    except Exception as e:
        logger.exception("Unexpected error while processing CV.")
        raise HTTPException(status_code=500, detail=str(e))
