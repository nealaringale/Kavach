# Kavach1930

AI-assisted cyber-fraud evidence organizer and incident-report drafting prototype.

> **Safety notice:** This is an educational prototype, not a fraud-verification service, legal authority, or emergency response system. AI assessments may be wrong. Verify facts independently. It does not file complaints, contact banks, or recover funds.

## MVP features

- Analyze pasted suspicious messages and fictional incident transcripts with Gemini.
- Explain possible warning signs and connect findings to source quotations.
- Locally redact several common PII patterns before the Gemini request, with a preview of minimized text.
- Use a Pydantic response schema and exact-source checks for selected quotations and transaction references.
- Draft an editable incident narrative with a 1,500-character target.
- Run a local heuristic scan for common instruction-override phrases (not a complete prompt-injection defense).
- Download a report draft.

Image/PDF uploads, audio analysis, external reporting integrations, and production-grade fraud classification are intentionally out of scope for this first version.

## Requirements

- Python 3.11+
- A Gemini API key from [Google AI Studio](https://aistudio.google.com/api-keys)
- VS Code or another Python editor

## Run locally on Windows

Open Command Prompt in this repository folder:

```bat
py -m venv .venv
.venv\Scripts\activate.bat
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
copy .env.example .env
```

Edit `.env` and add your key:

```dotenv
GEMINI_API_KEY=your_actual_key_here
GEMINI_MODEL=gemini-3.8-flash
```

Then start the app:

```bat
python -m streamlit run app.py
```

If your key or account cannot access the configured model, check available models and usage limits in Google AI Studio and set `GEMINI_MODEL` to a model available to your project.

## Privacy and security

- Do not upload real Aadhaar/PAN numbers, banking credentials, or sensitive victim documents to this demo.
- The text submitted for analysis is sent to the configured Gemini API.
- Keep `.env` out of Git. Never commit API keys.
- Extracted values are candidates, not proof that a transaction occurred.
- The local PromptShield scan uses simple patterns and is not a complete prompt-injection defense.
- PII redaction is heuristic and cannot catch every identifier. The minimized text is still sent to the configured Gemini API.
- Review all generated content before using it in a real report.

## Official reporting (India)

For real financial cyber-fraud incidents, contact the national cybercrime helpline at **1930** and use the [National Cyber Crime Reporting Portal](https://cybercrime.gov.in/). This prototype does not replace official advice or reporting channels.

## Engineering quality

- Typed response contract: see [kavach_schema.py](kavach_schema.py).
- Local utilities and deterministic checks: see [kavach_utils.py](kavach_utils.py).
- Unit tests: run `python -m pytest -q`.
- CI runs linting, Bandit static security checks, a dependency audit, compilation, and tests.
- Architecture and residual risks: [ARCHITECTURE.md](ARCHITECTURE.md) and [SECURITY.md](SECURITY.md).

## Google Cloud deployment

A non-root container and Cloud Run deployment guide are provided. The guide keeps the service private by default and uses Secret Manager for the Gemini API key.

See [GCP_DEPLOYMENT.md](GCP_DEPLOYMENT.md). Cloud deployment may incur charges; check billing and pricing first.

## Current status

MVP under active development. The repository has automated checks, but always review the latest [GitHub Actions results](https://github.com/nealaringale/Kavach/actions) and run the app locally with fictional examples before a live demonstration or deployment.
