# Averis Project Structure

Use this as the quick orientation map before changing code. The app is a FastAPI
MVP for classifying shipping emails, importing hackathon inbox data, tracking
documents, and preparing later SI/BL verification phases.

## Start Here

- `app/main.py` is the FastAPI entrypoint. It creates the app, initializes the
  database on startup, mounts static files, and includes all routers.
- `app/config.py` loads configurable settings from `.env` and environment
  variables. Real environment variables override `.env` values.
- `app/database.py` owns the SQLAlchemy engine/session setup and table creation.
- `routers/api.py` contains machine-facing endpoints for import, classification,
  and classification summaries.
- `GET /classification` is the human workbench for browsing classified emails.
- `services/email_classifier.py` contains the high-level classification decision
  flow.

## Directory Map

```text
Averis_Project/
├── app/
│   ├── main.py              FastAPI app setup, router registration, health check
│   ├── config.py            .env loading and Settings model
│   └── database.py          SQLAlchemy engine, sessions, init_db
├── models/
│   ├── email_message.py     EmailMessage ORM model and classification fields
│   ├── document.py          Document ORM model for imported/uploaded attachments
│   └── verification.py      Verification ORM model for later comparison results
├── routers/
│   ├── dashboard.py         HTML dashboard and classification workbench
│   ├── upload.py            HTML upload page and upload handling
│   ├── emails.py            JSON email list/detail endpoints
│   ├── documents.py         JSON document list endpoint
│   └── api.py               Import, classify, and reclassify API endpoints
├── services/
│   ├── classification_schema.py  Category constants and ClassificationResult
│   ├── classification_workbench.py  Grouped data for the classification UI
│   ├── email_classifier.py       DeepSeek-first classifier plus rule fallback tools
│   ├── llm_service.py            DeepSeek API integration
│   ├── input_importer.py         Imports root bundle inbox/attachments into SQLite
│   ├── inbox_service.py          Wrapper around root loader.py
│   ├── comparison_engine.py      SI vs BL field comparison scaffold
│   ├── document_parser.py        Future document extraction seam
│   └── ocr_service.py            Future OCR seam
├── scripts/
│   └── import_input_data.py      CLI wrapper for importing inbox data
├── templates/
│   ├── dashboard.html       Dashboard UI
│   ├── classification.html  Classified email workbench
│   └── upload.html          Upload UI
├── static/
│   └── styles.css           Shared page styling
├── tests/
│   └── test_email_classification.py  Unit tests for classification behavior
├── .env                     Local secrets/config, ignored by git
├── .env.example             Safe template of supported config values
├── requirements.txt         Python dependencies
└── README.md                Human setup/run notes
```

## Runtime Flow

### App Startup

1. `uvicorn app.main:app --reload`
2. `app/main.py` loads `settings = get_settings()` from `app/config.py`.
3. Startup lifespan creates `settings.upload_dir`.
4. Startup calls `init_db()` from `app/database.py`.
5. Routers from `routers/` are mounted on the FastAPI app.

### Configuration Flow

1. `.env` is read by `app/config.py`.
2. Values are copied into `os.environ` only if they are not already set.
3. `Settings` exposes:
   - `APP_NAME`
   - `APP_VERSION`
   - `DATABASE_URL`
   - `DATA_SOURCE`
   - `UPLOAD_DIR`
   - `DEEPSEEK_API_KEY`
   - `DEEPSEEK_BASE_URL`
   - `DEEPSEEK_MODEL`
   - `DEEPSEEK_TIMEOUT_SECONDS`
4. `services/llm_service.py` uses the DeepSeek settings.

### Import Bundle Data

Endpoint:

```text
POST /api/import-input-data?reset=true
```

Code path:

```text
routers/api.py
└── InputDataImporter.import_all()
    ├── InboxService.list_emails()
    │   └── root loader.py reads inbox/*.json
    ├── _upsert_email() -> models/email_message.py
    ├── _upsert_document() -> models/document.py
    └── _classify_email()
        └── EmailClassifier.classify()
```

CLI equivalent:

```text
scripts/import_input_data.py --reset
```

### Email Classification

Endpoints:

```text
POST /api/classify-email
POST /api/classify-imported-emails
GET  /api/classification-summary
GET  /classification
```

Code path:

```text
routers/api.py
└── EmailClassifier.classify()
    ├── if DEEPSEEK_API_KEY is missing:
    │   └── returns category=null, source=missing_ai_key,
    │       reason="AI key not included"
    ├── if key exists:
    │   └── LLMService.classify_email()
    │       └── POST {DEEPSEEK_BASE_URL}/chat/completions
    └── if DeepSeek fails or returns invalid category:
        └── rule result is stored with source=rules_fallback
```

Rule-only behavior is still available through
`EmailClassifier(prefer_llm=False)` and is covered by tests.

### Classified Email Workbench

Endpoint/UI:

```text
GET /classification
GET /classification?category=SI_REQUEST
```

Code path:

```text
routers/dashboard.py
└── get_classification_view_model()
    └── services/classification_workbench.py
        ├── groups official categories
        ├── separates missing-key/null-category emails
        └── prepares Phase 5-10 placeholder pipeline stages
```

The default category is `BL_COMPARISON` because it feeds the document
verification pipeline.

### Manual Upload Flow

Endpoint/UI:

```text
GET  /upload
POST /upload
```

Code path:

```text
routers/upload.py
├── reads uploaded email JSON
├── saves SI/BL files into UPLOAD_DIR
├── _upsert_email() -> EmailMessage
├── _upsert_document() -> Document
└── _classify_email() -> EmailClassifier
```

Uploads are classified the same way imported emails are classified.

### Email and Document Viewing

Endpoints:

```text
GET /emails
GET /emails/{email_id}
GET /documents
```

Code path:

```text
routers/emails.py      returns EmailMessage data plus classification fields
routers/documents.py   returns Document rows
```

Key output fields for classification:

```text
category
classification_confidence
classification_source
classified_at
```

## Data Model Links

- `EmailMessage` has many `Document` rows through `email_id`.
- `EmailMessage` has many `Verification` rows through `email_id`.
- `Document` may have many `Verification` rows through `document_id`.
- `Verification` is intended for later SI/BL comparison status, mismatch fields,
  confidence, and reviewer status.

## Hackathon Bundle Links

The parent folder contains the input bundle:

```text
../loader.py
../inbox/*.json
../attachments/*
../sample_submission.json
```

`DATA_SOURCE` points to that parent folder by default. `InboxService` imports
`loader.py` dynamically from `DATA_SOURCE`.

## Common Commands

```powershell
# Run app
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload

# Import/reimport bundle data
.\.venv\Scripts\python.exe scripts\import_input_data.py --reset

# Run tests
.\.venv\Scripts\python.exe -m unittest discover -s tests

# Compile check
.\.venv\Scripts\python.exe -m compileall app models routers services scripts tests
```

## Agent Notes

- Do not commit `.env`, `averis.db`, `uploads/`, `.venv/`, or `__pycache__/`.
- Add new user-facing API routes in `routers/api.py` unless they are HTML page
  routes.
- Add persistent entities in `models/`, then ensure `app/database.py` imports
  the model in `init_db()`.
- Put business logic in `services/`, not directly in routers.
- Keep category names exactly as the hackathon contract expects:
  `BL_COMPARISON`, `SI_REQUEST`, `INVOICE_QUERY`, `GENERAL`, `SPAM`.
- The comparison/extraction phases are scaffolded but not complete yet; prefer
  extending `services/document_parser.py`, `services/comparison_engine.py`, and
  `models/verification.py` for those phases.
