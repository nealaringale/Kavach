# Deploy Kavach1930 to Google Cloud Run

This guide is for a demo deployment. Do not upload real victim evidence to a public demo.

## Architecture

Browser → Streamlit app on Cloud Run → Gemini API

- Cloud Run builds and serves the container.
- Gemini analyzes the submitted, locally redacted text.
- The runtime API key is stored in Secret Manager.
- No report database is configured; report drafts stay in the user's current app session unless downloaded by the user.

## Prerequisites

1. Install the Google Cloud CLI: https://cloud.google.com/sdk/docs/install
2. Create/select a Google Cloud project and verify billing settings.
3. Create a Gemini API key in Google AI Studio: https://aistudio.google.com/api-keys
4. Sign in and select the project:

\`\`\`powershell
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
gcloud services enable run.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com secretmanager.googleapis.com
\`\`\`

Cloud Run deployment and container/image storage may incur costs. Check pricing and billing before deploying.

## Create the secret

Create a local file outside this repository named \`gemini-key.txt\` containing only the API key. Do not commit it. Then run:

\`\`\`powershell
gcloud secrets create kavach-gemini-api-key --replication-policy=automatic --data-file=gemini-key.txt
Remove-Item .\\gemini-key.txt
\`\`\`

If the secret already exists, add a new version instead:

\`\`\`powershell
gcloud secrets versions add kavach-gemini-api-key --data-file=gemini-key.txt
Remove-Item .\\gemini-key.txt
\`\`\`

Grant the Cloud Run runtime service account access to this secret using the least-privilege \`roles/secretmanager.secretAccessor\` role. Use a dedicated runtime service account when possible. Find the service identity and IAM steps in the official docs:

- https://cloud.google.com/run/docs/configuring/services/secrets
- https://cloud.google.com/secret-manager/docs/best-practices

## Deploy

From the repository root, run:

\`\`\`powershell
gcloud run deploy kavach1930 --source . --region asia-south1 --set-secrets=GEMINI_API_KEY=kavach-gemini-api-key:1 --set-env-vars=GEMINI_MODEL=gemini-3.8-flash --no-allow-unauthenticated
\`\`\`

The command above leaves the service private. This is safer by default. If a public judging URL is required, make a deliberate access decision with the organizer and configure authentication, quotas, and abuse protections before allowing unauthenticated access. A public endpoint that calls a paid or quota-limited model can be abused.

Use \`gcloud run services proxy kavach1930 --region asia-south1\` to access a private service locally after authenticating with the Google Cloud CLI.

## Verify

1. Open the service using the authenticated proxy.
2. Load the built-in fictional demo case.
3. Test a benign notice, a coercive scam sample, and an ambiguous case.
4. Check the Cloud Run logs for errors. Do not log submitted evidence or API keys.
5. Review the prompt-injection panel and explain that pattern matching is a heuristic, not a security guarantee.

## Before any real deployment

- Restrict service access and add request quotas/rate limiting.
- Add an appropriate privacy notice and data-retention policy.
- Review Google's current Gemini API data handling terms for your account.
- Review generated outputs manually; do not claim a definitive fraud verdict or legal validity.
- Consider Secret Manager version rotation, a dedicated service identity, and minimal IAM permissions.
