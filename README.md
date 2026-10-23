# Kavach1930

AI-assisted cyber-fraud evidence organizer and incident-report drafting prototype.

> **Safety notice:** This is an educational prototype, not a fraud-verification service, legal authority, or emergency response system. AI assessments may be wrong. Verify facts independently. It does not file complaints, contact banks, or recover funds.

## MVP features

- Analyze pasted suspicious messages and fictional incident transcripts with Gemini.
- Explain warning signs and connect them to exact evidence quotations.
- Extract transaction references and only retain values that can be matched to source text.
- Draft an incident narrative with a 1,500-character counter.
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
- The local PromptShield scan uses simple patterns and must not be described as complete or guaranteed protection.
- Review all generated content before using it in a real report.

## Official reporting (India)

For real financial cyber-fraud incidents, contact the national cybercrime helpline at **1930** and use the [National Cyber Crime Reporting Portal](https://cybercrime.gov.in/). This prototype does not replace official advice or reporting channels.

## Current status

Initial MVP scaffold. The app should be tested locally with fictional examples before a live demonstration or deployment.
