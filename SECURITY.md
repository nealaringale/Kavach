# Security policy and demo safeguards

## Intended use

Kavach1930 is an educational prototype for fictional or de-identified cyber-fraud examples. It is not an official fraud detector, legal service, police tool, bank service, or emergency reporting channel.

## Data handling

1. A user's text is held in the current Streamlit session.
2. Before the Gemini request, a local heuristic masks common patterns such as PAN-shaped identifiers, labelled Aadhaar/account/card numbers, email addresses, and Indian mobile numbers.
3. The minimized text is sent to the configured Gemini API. Redaction can miss identifiers and may mask benign content.
4. The app does not intentionally write the evidence to a local database or application log.
5. The user can download a report draft; downloaded files are then under the user's control.

Do not use real Aadhaar/PAN details, banking credentials, or sensitive victim evidence in a competition demo.

## Responsible reporting

For an actual incident in India, contact the national cybercrime helpline at **1930** and visit https://cybercrime.gov.in/. The app does not file a complaint or freeze a payment.

## Reporting a security issue

Please do not include real personal data, credentials, API keys, or victim documents in public issues. If a key is exposed, revoke it in Google AI Studio and rotate it in every place where it was used.

## Known limitations

- Local PII detection is regex-based and incomplete.
- PromptShield uses phrase-pattern matching and is not a complete prompt-injection defense.
- Exact-source matches do not prove the truth or authenticity of an extracted claim.
- AI output may be incorrect or incomplete; human review is required.
- Before public deployment, add suitable access controls, quotas/rate limiting, abuse monitoring, and a reviewed privacy/data-retention policy.
