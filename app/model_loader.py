# from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline

# MODEL_NAME = "yashpwr/resume-ner-bert-v2"

# print("Loading model... This may take a while the first time.")

# tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
# model = AutoModelForTokenClassification.from_pretrained(MODEL_NAME)

# # Print model labels for debugging
# print(f"Model labels: {model.config.id2label}")

# ner_pipeline = pipeline(
#     "ner",
#     model=model,
#     tokenizer=tokenizer,
#     aggregation_strategy="simple",
#     device=-1  # Force CPU
# )

# print("Model loaded successfully")

from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline
import re

# Use a better general-purpose NER model
MODEL_NAME = "dslim/bert-base-NER"  # Supports: PER, ORG, LOC, MISC

print("Loading model... This may take a while the first time.")

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForTokenClassification.from_pretrained(MODEL_NAME)

# Print model labels for debugging
print(f"Model labels: {model.config.id2label}")

ner_pipeline = pipeline(
    "ner",
    model=model,
    tokenizer=tokenizer,
    aggregation_strategy="simple",
    device=-1  # Force CPU
)

print("Model loaded successfully")


def extract_skills_from_text(text: str) -> list:
    """
    Extract skills from text using section-based parsing.
    Works for ANY industry by finding the skills section.
    """
    skills = []

    # Common skill section headers (case-insensitive)
    skill_headers = [
        r'(?:technical\s+)?skills?',
        r'core\s+(?:competenc(?:ies|y)|skills?)',
        r'key\s+skills?',
        r'proficiencies',
        r'expertise',
        r'tools?\s+(?:and|&)\s+technologies',
        r'technical\s+expertise',
        r'areas?\s+of\s+expertise'
    ]

    # Try to find skills section
    for header_pattern in skill_headers:
        # Match section with content until next section or end
        pattern = rf'(?i){header_pattern}\s*[:\-]?\s*(.*?)(?=\n\s*(?:[A-Z][A-Za-z\s]+:|$)|\Z)'
        match = re.search(pattern, text, re.DOTALL)

        if match:
            skills_text = match.group(1)

            # Extract individual skills (separated by comma, bullet, newline, or pipe)
            skill_items = re.split(r'[,•·\|\n]+', skills_text)

            for item in skill_items:
                # Clean and validate skill
                skill = item.strip()
                skill = re.sub(r'^[\-\*\d\.\)]+\s*', '',
                               skill)  # Remove bullets/numbers

                # Filter valid skills (2-50 chars, not just numbers/symbols)
                if 2 <= len(skill) <= 50 and re.search(r'[a-zA-Z]', skill):
                    skills.append(skill)

    return list(set(skills))  # Remove duplicates


def extract_email(text: str) -> list:
    """Extract email addresses"""
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    return list(set(re.findall(email_pattern, text)))


def extract_phone(text: str) -> list:
    """Extract phone numbers (international formats)"""
    phone_patterns = [
        # International
        r'\+?\d{1,3}[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}',
        r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',  # US format
    ]

    phones = []
    for pattern in phone_patterns:
        matches = re.findall(pattern, text)
        phones.extend(matches)

    return list(set(phones))


def extract_education_degree(text: str) -> list:
    """Extract education degrees"""
    degree_patterns = [
        r'\b(?:Bachelor|Master|PhD|Doctorate|Associate|Diploma|Certificate)(?:\s+of\s+|\s+in\s+|\s+)(?:Science|Arts|Engineering|Business|Technology|Education|[A-Z][a-z]+)',
        r'\b(?:B\.?S\.?|M\.?S\.?|B\.?A\.?|M\.?A\.?|MBA|PhD|Ph\.D\.?)(?:\s+in\s+[A-Z][a-z\s]+)?',
    ]

    degrees = []
    for pattern in degree_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        degrees.extend(matches)

    return list(set(degrees))
