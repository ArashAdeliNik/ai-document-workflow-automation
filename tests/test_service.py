import importlib


def test_ingestion_is_idempotent(tmp_path, monkeypatch):
    monkeypatch.setenv("DATA_DIR", str(tmp_path))
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{tmp_path / 'test.db'}")
    import app.config
    import app.database
    import app.service

    importlib.reload(app.config)
    importlib.reload(app.database)
    importlib.reload(app.service)
    app.database.init_db()
    content = b"INVOICE\nInvoice Number: I-1\nVendor: Demo\nTotal Amount: $100\nDate: 2026-01-01"
    first, duplicate1 = app.service.ingest("invoice.txt", content)
    second, duplicate2 = app.service.ingest("invoice.txt", content)
    assert duplicate1 is False
    assert duplicate2 is True
    assert first.id == second.id
