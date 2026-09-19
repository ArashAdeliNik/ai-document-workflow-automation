# Architecture Notes

## Components

| Component | Responsibility |
|---|---|
| FastAPI | Upload, registry, and review endpoints |
| Processor | Text extraction, classification, field extraction, confidence |
| Service | Duplicate control and workflow routing |
| SQLite | Document metadata, extracted fields, and audit state |
| Streamlit | Operations metrics and human-review queue |

## Confidence routing

The score blends classification evidence (65%) with extraction completeness (35%). The default threshold is 0.78 and can be changed through `REVIEW_THRESHOLD`. This is a transparent demo policy, not a calibrated production probability.

## Security boundaries

Uploaded names are normalized, accepted extensions are explicit, maximum file size is configurable, and public samples contain no real information. Production requires malware scanning, authentication, authorization, encryption, retention policies, and isolated object storage.
