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

def normalize_text(s):
    if not isinstance(s, str):
        return ""
    s = unicodedata.normalize("NFKD", s)
    s = s.replace("\xa0", " ")
    return s.strip()

def clean_text(s):
    s = unicodedata.normalize("NFKD", s)
    s = s.replace("\xa0", " ")
    return re.sub(r"[^a-zA-Z0-9\s.&-]", "", s).strip()

# NOTE: removed CSV/company-list loading for simplicity. The extractor now
# relies on spaCy NER, capitalization heuristics, and an optional AI fallback.

def extract_company_name(query):
    """Extract a company name from a user query.

    Heuristics (in order):
    1. spaCy NER (ORG)
    2. Capitalized word heuristic
    3. Optional AI-backed Grok extraction (if API key available)
    """
    query_clean = clean_text(query)

    # 1) spaCy NER
    try:
        doc = nlp(query_clean)
        orgs = [ent.text.strip() for ent in doc.ents if ent.label_ == "ORG"]
        if orgs:
            return normalize_text(orgs[0])
    except Exception:
        pass

    # 2) Capitalized fallback
    caps = re.findall(r"\b[A-Z][a-zA-Z0-9.&-]+\b", query_clean)
    caps = [c for c in caps if c not in GARBAGE]
    if caps:
        return caps[0]

    # 3) AI-backed fallback: ask Grok to extract the company
    try:
        api_key = os.environ.get('OPENAI_API_KEY') or os.environ.get('OPENROUTER_API_KEY')
        base_url = os.environ.get('OPENAI_BASE_URL')
        if not api_key:
            try:
                from src.core import pipeline
                api_key = getattr(pipeline, 'OPENROUTER_API_KEY', None)
                base_url = getattr(pipeline, 'OPENAI_BASE_URL', base_url)
            except Exception:
                pass

        if api_key and OpenAI is not None:
            client = OpenAI(base_url=base_url or 'https://openrouter.ai/api/v1', api_key=api_key)
            prompt = (
                f"Extract the primary company or organization mentioned in the user query below.\n"
                f"If there is no clear company, reply with the single token NONE.\n\n"
                f"User query: {query}\n\n"
                f"Respond with only the company name exactly as it should appear (no extra text)."
            )

            try:
                resp = client.chat.completions.create(
                    model="x-ai/grok-4.1-fast",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=60,
                )
                content = getattr(resp.choices[0].message, 'content', '') or ''
                content = content.strip().strip('"')
                if content and content.upper() != 'NONE':
                    detected = normalize_text(content)
                    if detected:
                        return detected
            except Exception:
                pass

    except Exception:
        pass

    return None
