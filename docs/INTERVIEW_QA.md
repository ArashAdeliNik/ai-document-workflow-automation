# Interview and Client Q&A

## Why not fully automate every document?

Incorrect document data can affect payments and legal operations. Confidence-based exception routing preserves speed without hiding uncertainty.

## Is this using a paid AI API?

No. The portfolio demo is deterministic, transparent, and free to run. Its boundaries are clear, and a production AI/OCR provider can be added behind the processing layer.

## How are duplicates prevented?

The system calculates SHA-256 over the file bytes and enforces uniqueness in the database.

## How would you scale it?

Use PostgreSQL, object storage, a job queue, asynchronous workers, OCR, centralized observability, and horizontal API/dashboard deployment.

## What is the most important engineering choice?

Uncertain results become visible work items rather than silently passing through the system.
