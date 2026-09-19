from datetime import UTC, datetime
from pathlib import Path

from sqlalchemy import select

from .config import REVIEW_THRESHOLD, UPLOAD_DIR
from .database import Document, SessionLocal
from .processor import extract_text, file_sha256, process_document


def ingest(filename: str, content: bytes) -> tuple[Document, bool]:
    digest = file_sha256(content)
    with SessionLocal() as session:
        existing = session.scalar(select(Document).where(Document.file_hash == digest))
        if existing:
            return existing, True
        safe_name = Path(filename).name
        path = UPLOAD_DIR / f"{digest[:12]}_{safe_name}"
        path.write_bytes(content)
        result = process_document(extract_text(path))
        item = Document(
            filename=safe_name,
            file_hash=digest,
            document_type=result.document_type,
            confidence=result.confidence,
            status="approved" if result.confidence >= REVIEW_THRESHOLD else "needs_review",
            summary=result.summary,
            extracted_data=result.fields,
        )
        session.add(item)
        session.commit()
        return item, False


def review(document_id: int, decision: str, note: str, corrections: dict | None) -> Document:
    if decision not in {"approved", "rejected"}:
        raise ValueError("Decision must be approved or rejected.")
    with SessionLocal() as session:
        item = session.get(Document, document_id)
        if not item:
            raise LookupError("Document not found.")
        if corrections:
            item.extracted_data = {**item.extracted_data, **corrections}
        item.status = decision
        item.reviewer_note = note
        item.reviewed_at = datetime.now(UTC)
        session.commit()
        return item
