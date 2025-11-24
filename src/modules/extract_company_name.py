import spacy
import pandas as pd
import re
import unicodedata
from difflib import SequenceMatcher
from pathlib import Path

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

# Load S&P 500 list
def load_sp500():
    try:
        # Try multiple paths to find the CSV
        possible_paths = [
            Path("data/companies.csv"),
            Path("../data/companies.csv"),
            Path("../../data/companies.csv"),
            Path("datasets/companies.csv"),
        ]
        
        for path in possible_paths:
            if path.exists():
                df = pd.read_csv(path)
                names = set(normalize_text(x) for x in df["Name"].astype(str).tolist())
                return names
        
        print("[WARNING] Could not find companies.csv. Proceeding without company list.")
        return set()
    except Exception as e:
        print(f"[WARNING] Error loading company list: {e}")
        return set()

ALL_COMPANIES = load_sp500()

# ROBUST COMPANY EXTRACTOR
def extract_company_name(query):
    query_clean = clean_text(query)
    q_low = query_clean.lower()

    best_match = None
    best_score = 0.0

    # Search each company
    for company in ALL_COMPANIES:
        comp_raw = normalize_text(company)
        comp_norm = comp_raw.lower()
        tokens = comp_norm.split()

        # Exact match
        if comp_norm == q_low:
            return comp_raw

        # Token based match
        for token in tokens:
            if len(token) > 2 and token in q_low:
                return comp_raw

        # Substring match
        if comp_norm in q_low:
            return comp_raw

        # Fuzzy match
        score = SequenceMatcher(None, comp_norm, q_low).ratio()
        if score > best_score:
            best_score = score
            best_match = comp_raw

    # Use fuzzy match if above threshold
    if best_score >= 0.7:
        return best_match

    # SpaCy fallback
    doc = nlp(query_clean)
    orgs = [ent.text.strip() for ent in doc.ents if ent.label_ == "ORG"]
    for org in orgs:
        o_low = org.lower()
        for company in ALL_COMPANIES:
            if o_low in company.lower():
                return company

    # Capitalized fallback
    caps = re.findall(r"\b[A-Z][a-zA-Z0-9.&-]+\b", query_clean)
    caps = [c for c in caps if c not in GARBAGE]
    if caps:
        return caps[0]

    return None
