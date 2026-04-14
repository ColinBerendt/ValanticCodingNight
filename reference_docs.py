import os
from pdf_extractor import extract_text

CASE_DIR = os.path.join(os.path.dirname(__file__), "Case 1 SFS - Automated CE Marking")

_cache: dict[str, str] = {}


def _load(filename: str) -> str:
    if filename not in _cache:
        path = os.path.join(CASE_DIR, filename)
        _cache[filename] = extract_text(path)
    return _cache[filename]


def get_ead_text() -> str:
    return _load("EAD 030351-00-0402.pdf")


def get_eta_text() -> str:
    return _load("ETA 23-0859.pdf")


def get_cpr_text() -> str:
    return _load("EU-CPR 305-2011.pdf")
