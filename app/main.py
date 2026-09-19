from typing import Annotated

from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from .config import MAX_FILE_MB
from .database import Document, SessionLocal, init_db
from .schemas import DocumentOut, ReviewRequest
from .service import ingest, review

app = FastAPI(title="Document Workflow Automation", version="1.0.0")


@app.on_event("startup")
def startup() -> None:
    init_db()


def get_session():
    with SessionLocal() as session:
        yield session


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/documents", response_model=list[DocumentOut])
def list_documents(session: Annotated[Session, Depends(get_session)], status: str | None = None):
    query = select(Document).order_by(Document.created_at.desc())
    if status:
        query = query.where(Document.status == status)
    return list(session.scalars(query))


@app.post("/documents", response_model=DocumentOut)
async def upload_document(file: Annotated[UploadFile, File()]):
    content = await file.read()
    if len(content) > MAX_FILE_MB * 1024 * 1024:
        raise HTTPException(413, "File too large")
    try:
        item, _ = ingest(file.filename or "document.txt", content)
        return item
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc


@app.post("/documents/{document_id}/review", response_model=DocumentOut)
def review_document(document_id: int, payload: ReviewRequest):
    try:
        return review(document_id, payload.decision, payload.note, payload.corrections)
    except LookupError as exc:
        raise HTTPException(404, str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc
