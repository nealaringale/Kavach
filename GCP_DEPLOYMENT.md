# Deploy Kavach1930 to Google Cloud Run

This guide is for a demo deployment. Do not upload real victim evidence to a public demo.

## Architecture

Browser → Streamlit on Cloud Run → Gemini API

- Cloud Run builds and serves the container.
- Before analysis, the app masks some common PII patterns locally.
- The runtime API key is stored in Secret Manager.
- No report database is configured; the draft remains in the current session unless downloaded.

## Prerequisites

1. Install the Google Cloud CLI: https://cloud.google.com/sdk/docs/install
2. Create/select a Google Cloud project and review billing.
3. Create a Gemini API key in Google AI Studio: https://aistudio.google.com/api-keys
4. Sign in and select your project:

~~~powershell
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
gcloud services enable run.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com secretmanager.googleapis.com
~~~

Cloud Run deployment and container/image storage may incur costs. Review current pricing before deployment.

## Create the secret

Create a local file outside this repository named gemini-key.txt containing only the API key. Do not commit it. Then run:

~~~powershell
gcloud secrets create kavach-gemini-api-key --replication-policy=automatic --data-file=gemini-key.txt
Remove-Item .\gemini-key.txt
~~~

If the secret already exists, add a new version instead:

~~~powershell
gcloud secrets versions add kavach-gemini-api-key --data-file=gemini-key.txt
Remove-Item .\gemini-key.txt
~~~

Grant the Cloud Run runtime service account the least-privilege roles/secretmanager.secretAccessor role on this secret. Use a dedicated runtime service account if possible. Official documentation:

- https://cloud.google.com/run/docs/configuring/services/secrets
- https://cloud.google.com/secret-manager/docs/best-practices

## Deploy

From the repository root:

~~~powershell
gcloud run deploy kavach1930 --source . --region asia-south1 --set-secrets=GEMINI_API_KEY=kavach-gemini-api-key:1 --set-env-vars=GEMINI_MODEL=gemini-3.8-flash --no-allow-unauthenticated
~~~

The command leaves the service private by default. A private service is safer than exposing an endpoint that can consume Gemini quota. If a public judging URL is required, make a deliberate access decision with the organizer and configure suitable authentication, quota limits, abuse protection, and cost monitoring before allowing unauthenticated access.

After deployment, use the authenticated Cloud Run service proxy as needed:

~~~powershell
gcloud run services proxy kavach1930 --region asia-south1
~~~

## Verification checklist

1. Open the service using the authenticated proxy.
2. Load the built-in fictional demo case.
3. Test a coercive-scam sample, a benign notice, and an ambiguous case.
4. Check Cloud Run logs for errors. Never log submitted evidence or API keys.
5. Explain that PromptShield's pattern checks are heuristics, not a security guarantee.

## Before real use

- Restrict access and add request quotas/rate limiting.
- Add and review a privacy notice and data-retention policy.
- Review Gemini API data handling terms for your account.
- Verify all generated details; do not claim definitive fraud detection, legal validity, or guaranteed recovery.
- Review secret version rotation, runtime identity, and minimal IAM permissions.
