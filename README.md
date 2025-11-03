# CV NLP Service - Repository Overview

This is a **FastAPI-based microservice** for extracting structured information from candidate resumes/CVs using Natural Language Processing (NER - Named Entity Recognition).

## 🎯 Purpose

Automates CV parsing for your job recruitment website by identifying and extracting key information like names, skills, education, experience, locations, contact details, etc. from candidate resumes across **all industries and professions**.

## 🏗️ Architecture

**Core Components:**

- `main.py` - FastAPI server with 2 endpoints:
  - `GET /` - Health check
  - `POST /extract` - Accepts CV files (PDF/TXT/DOCX) or plain text, returns extracted entities
- `model_loader.py` - Loads the pre-trained BERT model `dslim/bert-base-NER` for general-purpose entity recognition plus custom extraction functions for skills, education, and contact information

## 📦 Tech Stack

- **FastAPI** - Web framework
- **Transformers (Hugging Face)** - NER pipeline
- **PyTorch (CPU)** - ML backend
- **Docker** - Containerization
- **PyPDF2** - PDF text extraction
- **python-docx** - DOCX text extraction

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- Docker (for containerized deployment)

### Local Development

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd Resume-NLP-Service
   ```

2. **Create virtual environment**

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**

   ```bash
   # Install PyTorch CPU version first
   pip install torch==2.1.0 --index-url https://download.pytorch.org/whl/cpu

   # Install other dependencies
   pip install -r requirements.txt
   ```

4. **Run the service**

   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

5. **Access the API**
   - API: http://localhost:8000
   - Swagger Docs: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

### Docker Deployment

1. **Build the Docker image**

   ```bash
   docker build -t cv-nlp-service .
   ```

   > ⚠️ **Note:** First build may take 5-10 minutes as it downloads the ML model (~400MB)

2. **Run the container**

   ```bash
   docker run -d -p 8000:8000 --name cv-service cv-nlp-service
   ```

3. **Check logs**

   ```bash
   docker logs -f cv-service
   ```

4. **Stop the container**
   ```bash
   docker stop cv-service
   docker rm cv-service
   ```

### Docker Compose (Optional)

Create a `docker-compose.yml`:

```yaml
version: "3.8"
services:
  cv-nlp-service:
    build: .
    ports:
      - "8000:8000"
    restart: unless-stopped
    environment:
      - LOG_LEVEL=INFO
```

Run with:

```bash
docker-compose up -d
```

## 📡 API Usage

### Health Check

```bash
curl http://localhost:8000/
```

### Extract Entities from Text

```bash
curl -X POST "http://localhost:8000/extract" \
  -F "text=John Doe is a Python Developer with 5 years experience in Django and FastAPI. He works at Google in San Francisco. Contact: john.doe@example.com, +1-555-0123. Education: Bachelor of Computer Science"
```

### Extract Entities from File (PDF/DOCX/TXT)

```bash
# PDF file
curl -X POST "http://localhost:8000/extract" \
  -F "file=@resume.pdf"

# DOCX file
curl -X POST "http://localhost:8000/extract" \
  -F "file=@resume.docx"

# Text file
curl -X POST "http://localhost:8000/extract" \
  -F "file=@resume.txt"
```

### Sample Response

```json
{
  "message": "Entity extraction successful",
  "entities": {
    "Name": ["John Doe"],
    "Organization": ["Google"],
    "Location": ["San Francisco"],
    "Skills": ["Python", "Django", "FastAPI", "REST API", "Docker", "Git"],
    "Email": ["john.doe@example.com"],
    "Phone": ["+1-555-0123"],
    "Education": ["Bachelor of Computer Science"]
  },
  "text_length": 256,
  "chunks_processed": 1
}
```

## 📥 Input/Output

**Input:**

- CV file (`.txt`, `.pdf`, `.docx`) OR
- Plain text content via form data
- Minimum 10 characters required

**Output:**

- Grouped entities in JSON format
- **Supported entity types:**
  - **Name** - Person names (extracted by NER)
  - **Organization** - Companies, institutions (extracted by NER)
  - **Location** - Cities, countries, addresses worldwide (extracted by NER)
  - **Skills** - Technical and professional skills from any industry (section-based extraction)
  - **Email** - Email addresses (regex-based extraction)
  - **Phone** - Phone numbers in international formats (regex-based extraction)
  - **Education** - Degrees, certifications (regex-based extraction)
  - **Other** - Miscellaneous entities (extracted by NER)

## 🎯 Key Features

### 1. **Universal Industry Support**

Works with CVs from **any profession**:

- Technology: Software Developer, DevOps Engineer, Data Scientist
- Healthcare: Doctor, Nurse, Medical Technician
- Business: Accountant, Marketing Manager, HR Specialist
- Education: Teacher, Professor, Academic Advisor
- And more...

### 2. **Global Location Recognition**

Extracts locations from **anywhere in the world**:

- Cities: New York, London, Tokyo, Mumbai, São Paulo
- Countries: United States, United Kingdom, Vietnam, Australia
- Regions: Silicon Valley, Bay Area, Southeast Asia

### 3. **Hybrid Extraction Approach**

Combines multiple techniques for accuracy:

- **NER Model** (`dslim/bert-base-NER`) - For names, organizations, locations
- **Section-based parsing** - Finds and extracts skills from CV sections
- **Regex patterns** - Extracts emails, phones, education degrees

### 4. **Multi-format Support**

Accepts various file formats:

- PDF documents (text-based)
- Microsoft Word (.docx)
- Plain text files (.txt)
- Direct text input

## 🐳 Image Size Optimization

This service uses:

- **Python 3.10-slim** base image
- **PyTorch CPU-only** version (~800MB vs 4GB CUDA)
- **Multi-stage Docker build** to reduce final image size
- **No cache** pip installations

Final image size: **~2-3GB** (down from ~7GB)

## 🔧 Configuration

Environment variables (optional):

```bash
# Port configuration
PORT=8000

# Logging level
LOG_LEVEL=INFO
```

## 🔍 How It Works

1. **Text Extraction**: Extracts text from uploaded file (PDF/DOCX) or uses provided text
2. **Text Cleaning**: Removes excessive whitespace and normalizes formatting
3. **Chunking**: Splits long text into 400-character chunks (BERT token limit)
4. **NER Processing**: Each chunk is processed by the BERT model to identify entities
5. **Section Parsing**: Skills section is located and parsed separately
6. **Regex Extraction**: Contact details and education are extracted using patterns
7. **Post-processing**: Results are cleaned, deduplicated, and grouped by entity type

## ⚠️ Limitations

- PDF text extraction works best with text-based PDFs (not scanned images)
- Skills extraction depends on proper section formatting in the CV
- Phone number patterns may not cover all international formats
- Very long CVs (>10 pages) may take longer to process
