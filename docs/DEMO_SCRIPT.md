# Five-Minute Demo Script

1. Explain the manual data-entry problem and the human-in-the-loop principle.
2. Open the dashboard and upload `sample_documents/invoice.txt`.
3. Show detected type, extracted fields, confidence, and registry entry.
4. Upload the same file again and explain SHA-256 idempotency.
5. Upload a vague document to trigger `needs_review`.
6. Approve or reject it with a reviewer note.
7. Open `/docs` and demonstrate the API contract.
8. Close with the production path: OCR, PostgreSQL, RBAC, object storage, and ERP integration.
