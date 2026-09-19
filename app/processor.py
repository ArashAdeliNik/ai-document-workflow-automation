import hashlib
import re
from dataclasses import dataclass
from pathlib import Path

from docx import Document as WordDocument
from pypdf import PdfReader


@dataclass(frozen=True)
class ProcessingResult:
    document_type: str
    confidence: float
    summary: str
    fields: dict[str, str | float | None]


TYPE_RULES = {
    "invoice": ("invoice", "invoice number", "total amount", "amount due", "فاکتور"),
    "contract": ("contract", "agreement", "effective date", "termination", "قرارداد"),
    "purchase_order": ("purchase order", "po number", "ship to", "خرید"),
}


def file_sha256(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def extract_text(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".txt":
        return path.read_text(encoding="utf-8")
    if suffix == ".pdf":
        return "\n".join(page.extract_text() or "" for page in PdfReader(path).pages)
    if suffix == ".docx":
        return "\n".join(p.text for p in WordDocument(path).paragraphs)
    raise ValueError("Unsupported file type. Use PDF, DOCX, or TXT.")


def _match(pattern: str, text: str) -> str | None:
    found = re.search(pattern, text, flags=re.IGNORECASE | re.MULTILINE)
    return found.group(1).strip() if found else None


def classify(text: str) -> tuple[str, float]:
    lowered = text.lower()
    scores = {kind: sum(term in lowered for term in terms) for kind, terms in TYPE_RULES.items()}
    kind = max(scores, key=scores.get)
    hits = scores[kind]
    if hits == 0:
        return "other", 0.45
    return kind, min(0.95, 0.58 + hits * 0.10)


def extract_fields(text: str, kind: str) -> dict[str, str | float | None]:
    common = {
        "date": _match(r"(?:date|effective date|تاریخ)\s*[:#-]?\s*([^\n]+)", text),
        "email": _match(r"([\w.+-]+@[\w.-]+\.[A-Za-z]{2,})", text),
    }
    if kind == "invoice":
        common.update(
            {
                "document_number": _match(r"(?:invoice\s*(?:number|no\.?|#)|شماره فاکتور)\s*[:#-]?\s*([\w-]+)", text),
                "vendor": _match(r"(?:vendor|supplier|فروشنده)\s*[:#-]?\s*([^\n]+)", text),
                "total_amount": _match(r"(?:total amount|amount due|grand total|مبلغ کل)\s*[:#-]?\s*([$€£]?\s?[\d,.]+)", text),
            }
        )
    elif kind == "contract":
        common.update(
            {
                "document_number": _match(r"(?:contract\s*(?:number|no\.?|#)|شماره قرارداد)\s*[:#-]?\s*([\w-]+)", text),
                "party_a": _match(r"(?:party a|first party|طرف اول)\s*[:#-]?\s*([^\n]+)", text),
                "party_b": _match(r"(?:party b|second party|طرف دوم)\s*[:#-]?\s*([^\n]+)", text),
                "end_date": _match(r"(?:end date|termination date|تاریخ پایان)\s*[:#-]?\s*([^\n]+)", text),
            }
        )
    elif kind == "purchase_order":
        common.update(
            {
                "document_number": _match(
                    r"(?:po\s*(?:number|no\.?|#)|purchase order\s*(?:number|#)|شماره سفارش)\s*[:#-]?\s*([\w-]+)", text
                ),
                "supplier": _match(r"(?:supplier|vendor|تامین کننده)\s*[:#-]?\s*([^\n]+)", text),
                "total_amount": _match(r"(?:total|order total|مبلغ کل)\s*[:#-]?\s*([$€£]?\s?[\d,.]+)", text),
            }
        )
    return common


def process_document(text: str) -> ProcessingResult:
    clean = " ".join(text.split())
    if len(clean) < 20:
        raise ValueError("Document contains too little readable text.")
    kind, class_confidence = classify(text)
    fields = extract_fields(text, kind)
    populated = sum(value is not None for value in fields.values())
    completeness = populated / max(1, len(fields))
    confidence = round(0.65 * class_confidence + 0.35 * completeness, 2)
    title = kind.replace("_", " ").title()
    summary = f"{title} detected; {populated} of {len(fields)} target fields extracted."
    return ProcessingResult(kind, confidence, summary, fields)
