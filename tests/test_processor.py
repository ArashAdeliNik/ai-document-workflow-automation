from app.processor import classify, file_sha256, process_document


def test_invoice_processing_extracts_fields():
    text = """INVOICE\nInvoice Number: INV-42\nDate: 2026-09-18
Vendor: Example Ltd\nEmail: finance@example.com\nTotal Amount: $1,250.00"""
    result = process_document(text)
    assert result.document_type == "invoice"
    assert result.fields["document_number"] == "INV-42"
    assert result.fields["vendor"] == "Example Ltd"
    assert result.confidence >= 0.75


def test_unknown_document_is_other():
    kind, confidence = classify("A general operational note without structured labels.")
    assert kind == "other"
    assert confidence < 0.5


def test_hash_is_deterministic():
    assert file_sha256(b"same") == file_sha256(b"same")
