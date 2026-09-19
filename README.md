# Averis Project

Phase 1 FastAPI foundation for the Shipping Document Verification AI.

## Run

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Then open `http://127.0.0.1:8000`.

## Import the hackathon input data

The root bundle contains `loader.py`, `inbox/`, `attachments/`, and
`sample_submission.json`. By default this app reads from the parent folder:

```bash
python scripts/import_input_data.py --reset
```

Use `DATA_SOURCE` if the bundle lives somewhere else:

```bash
set DATA_SOURCE=C:\path\to\sdoc-hackathon-bundle
python scripts/import_input_data.py --reset
```

After importing, check:

- `GET /emails`
- `GET /emails/email_004`
- `GET /documents`

## Structure

- `app/`: FastAPI entrypoint, configuration, and database setup.
- `models/`: SQLAlchemy ORM models for documents and verifications.
- `routers/`: Dashboard, document, and API routes.
- `services/`: Email classification, parsing, OCR, LLM, and comparison service seams.
- `templates/` and `static/`: Initial dashboard page assets.
