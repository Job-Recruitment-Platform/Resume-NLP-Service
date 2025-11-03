# CV NLP Service - Repository Overview

This is a **FastAPI-based microservice** for extracting structured information from candidate resumes/CVs using Natural Language Processing (NER - Named Entity Recognition).

## 🎯 Purpose

Automates CV parsing for your job recruitment website by identifying and extracting key information like names, skills, education, experience, etc. from candidate resumes.

## 🏗️ Architecture

**Core Components:**

- `main.py` - FastAPI server with 2 endpoints:
  - `GET /` - Health check
  - `POST /extract` - Accepts CV files (PDF/TXT/DOCX) or plain text, returns extracted entities
- `model_loader.py` - Loads the pre-trained BERT model `yashpwr/resume-ner-bert-v2` for resume entity recognition

## 📦 Tech Stack

- **FastAPI** - Web framework
- **Transformers (Hugging Face)** - NER pipeline
- **PyTorch (CPU)** - ML backend
- **Docker** - Containerization

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
  -F "text=John Doe, Python Developer with 5 years experience in Django and FastAPI"
```

### Extract Entities from File

```bash
curl -X POST "http://localhost:8000/extract" \
  -F "file=@resume.txt"
```

### Sample Response

```json
{
  "message": "Entity extraction successful",
  "entities": {
    "NAME": ["John Doe"],
    "SKILLS": ["Python", "Django", "FastAPI"],
    "EXPERIENCE": ["5 years"]
  }
}
```

## 📥 Input/Output

**Input:**

- CV file (`.txt`, `.pdf`, `.docx`) OR
- Plain text content via form data

**Output:**

- Grouped entities in JSON format
- Supported entity types: NAME, SKILLS, EDUCATION, EXPERIENCE, etc.

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
