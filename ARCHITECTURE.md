# Kavach1930 architecture and design decisions

## Problem

People facing possible coercive cyber-fraud often have unstructured messages and payment alerts, but need to identify warning signs, organize facts, and prepare an incident summary quickly.

## MVP approach

Kavach1930 accepts plain text evidence and asks Gemini for a bounded, typed analysis. It then validates the response schema and checks whether key quotes and transaction references can be matched to the minimized source text.

~~~mermaid
flowchart TD
    A[User enters text evidence] --> B[Input length bound]
    B --> C[Local PII minimization]
    C --> D[Preview of text to be sent]
    D --> E[Gemini API]
    E --> F[Pydantic structured response validation]
    F --> G[Exact-source checks for quotes and references]
    G --> H[Human-reviewed incident draft]
    I[Local PromptShield phrase scanner] --> J[Potential injection signals]
~~~

## Boundaries

- Gemini performs language understanding and summarization. It is not the source of legal truth.
- Python and Pydantic validate response structure; exact-substring matching checks that selected quotes and references appear in the minimized input.
- Local PromptShield looks for configured phrases only. It is not a complete classifier or a full prompt-injection defense.
- A matching string is not proof of an actual transaction.
- Generated findings require human review. The app does not submit a report, contact banks, or guarantee recovery.

## Security and privacy decisions

- The app never intentionally logs submitted evidence or API keys.
- Common Indian identifiers (PAN-shaped strings, labelled Aadhaar/account/card numbers, emails, and Indian mobile numbers) are redacted before text is sent to Gemini.
- Redaction is heuristic and cannot identify every personal detail. Avoid real victim documents and credentials in the demo.
- The source is sent to a third-party Gemini API after minimization. The operator must review current API terms and data handling settings.
- The API key is loaded from local .env for development. .env is ignored by Git.
- The Cloud Run guide uses Secret Manager and leaves service access private by default.
- The container runs as a non-root user and excludes local secrets and tests from the image build context.

## Threat model

| Threat | MVP control | Residual risk |
|---|---|---|
| Prompt injection in evidence | System instruction treats evidence as untrusted; local phrase scanner surfaces some patterns | Model behavior cannot be guaranteed; scanner can miss obfuscated attacks |
| Invented transaction details | Typed schema, exact-source checks, empty values for missing data | Exact matches do not prove authenticity; non-transaction fields need review |
| Accidental PII disclosure | Local heuristic redaction and a preview of minimized text | Redaction is not exhaustive; users may submit other sensitive data |
| Malicious or malformed model output | JSON response mode, Pydantic schema, normalization bounds | Unexpected API errors and model behavior still require graceful handling |
| Leaked API key | .env ignored; Secret Manager deployment guide | Local endpoint, shell history, or misconfigured cloud permissions can still leak secrets |
| Public endpoint abuse | GCP guide deploys privately by default | Public demo requires access controls, quota monitoring and cost limits |

## Key engineering trade-offs

The MVP uses one Gemini request, not a multi-agent workflow. The goal is to keep latency, cost, and failure modes understandable. It prefers explicit uncertainty and source checks over pretending to make a definitive legal or fraud determination.
