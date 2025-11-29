import spacy
import re
import unicodedata
import os
from typing import Optional
from difflib import SequenceMatcher
from dotenv import load_dotenv

# Load environment variables (.env must be in project root)
load_dotenv()

# Optional OpenAI client for AI-backed extraction
try:
    from openai import OpenAI
except Exception:
    OpenAI = None

# Load spaCy
nlp = spacy.load("en_core_web_sm")

# Ignore words that are not company names
GARBAGE = {
    "Tell", "Give", "Show", "Provide", "Explain",
    "Me", "Info", "Information", "Details", "About",
    "Something", "Somthing", "Please", "Some", "Aomthing"
}

def normalize_text(text: str) -> str:
    text = text.strip()
    text = re.sub(r"[^a-zA-Z0-9 .&-]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text

def clean_text(s):
    s = unicodedata.normalize("NFKD", s)
    s = s.replace("\xa0", " ")
    return re.sub(r"[^a-zA-Z0-9\s.&-]", "", s).strip()

# NOTE: removed CSV/company-list loading for simplicity. The extractor now
# relies on spaCy NER, capitalization heuristics, and an optional AI fallback.

def extract_company_name(query):
    api_key = (
        os.environ.get("OPENAI_API_KEY")
        or os.environ.get("OPENROUTER_API_KEY")
    )
    base_url = os.environ.get("OPENAI_BASE_URL", "https://openrouter.ai/api/v1")

    if not api_key or OpenAI is None:
        return None

    client = OpenAI(base_url=base_url, api_key=api_key)

    prompt = (
        "Extract the company name from the query.\n"
        "Output ONLY the name.\n"
        "No punctuation. No quotes. No extra text.\n"
        "If no company exists, return NONE.\n"
        f"Query: {query}"
    )

    try:
        resp = client.chat.completions.create(
            model="x-ai/grok-4.1-fast",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=20
        )
        content = getattr(resp.choices[0].message, "content", "")
        if not content:
            return None
        raw = content.strip()
    except:
        return None

    if raw.upper() == "NONE":
        return None

    name = normalize_text(raw)
    return name if name else None
