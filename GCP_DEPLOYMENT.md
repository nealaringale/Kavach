# Deploy Kavach1930 to Google Cloud Run

This guide is for a demo deployment. Do not upload real victim evidence to a public demo.

## Deploy from GitHub Actions (recommended)

The repository includes a manual workflow at **Actions → Deploy Kavach1930 to Google Cloud Run → Run workflow**. It is intentionally manual rather than automatically publishing a public app on every commit. It syncs the existing GitHub Actions secret `GEMINI_API_KEY` to Google Secret Manager, builds from the repository, and deploys to Cloud Run.

### GitHub repository configuration

Under **Settings → Secrets and variables → Actions**, add one repository secret:

- `GEMINI_API_KEY` (preferred), or `GOOGLE_API_KEY`: your Gemini API key from Google AI Studio. Never put it in a source file or repository variable. The workflows accept either name.

Add these repository variables:

- `GCP_PROJECT_ID`: your Google Cloud project ID.
- `GCP_WIF_PROVIDER`: the full Workload Identity Provider resource name.
- `GCP_DEPLOY_SERVICE_ACCOUNT`: service account impersonated by GitHub Actions.
- `GCP_RUN_SERVICE_ACCOUNT`: service account used by the running Cloud Run service.
- `GCP_REGION`: optional; defaults to `asia-south1`.
- `GEMINI_MODEL`: optional; defaults to `gemini-3.8-flash`.

### Configure Workload Identity Federation

Use Workload Identity Federation instead of a long-lived Google service-account key. The following commands are a starting template; run them from an administrator-authenticated terminal and replace `YOUR_PROJECT_ID` and `YOUR_DEPLOY_SERVICE_ACCOUNT`.

~~~bash
gcloud config set project YOUR_PROJECT_ID
gcloud services enable iam.googleapis.com iamcredentials.googleapis.com sts.googleapis.com run.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com secretmanager.googleapis.com

PROJECT_NUMBER="$(gcloud projects describe YOUR_PROJECT_ID --format='value(projectNumber)')"
DEPLOY_SA="YOUR_DEPLOY_SERVICE_ACCOUNT"
POOL="github-actions"
PROVIDER="kavach-main"

gcloud iam workload-identity-pools create "$POOL" --project=YOUR_PROJECT_ID --location=global --display-name="GitHub Actions"
gcloud iam workload-identity-pools providers create-oidc "$PROVIDER" --project=YOUR_PROJECT_ID --location=global --workload-identity-pool="$POOL" --display-name="Kavach main branch" --issuer-uri="https://token.actions.githubusercontent.com" --attribute-mapping="google.subject=assertion.sub,attribute.repository=assertion.repository,attribute.ref=assertion.ref" --attribute-condition="assertion.repository == 'nealaringale/Kavach' && assertion.ref == 'refs/heads/main'"

gcloud iam service-accounts add-iam-policy-binding "$DEPLOY_SA" --project=YOUR_PROJECT_ID --role="roles/iam.workloadIdentityUser" --member="principalSet://iam.googleapis.com/projects/$PROJECT_NUMBER/locations/global/workloadIdentityPools/$POOL/attribute.repository/nealaringale/Kavach"
~~~

The provider resource name is:

~~~text
projects/PROJECT_NUMBER/locations/global/workloadIdentityPools/github-actions/providers/kavach-main
~~~

Use that exact resource format, with the real project number, as `GCP_WIF_PROVIDER`.

The deploy service account needs permission to deploy Cloud Run from source, build and store the container, create/update the Gemini secret, bind access to that secret, and act as the runtime service account. Review and grant the minimum appropriate IAM roles for your project; these permissions are powerful. The runtime service account should receive only `roles/secretmanager.secretAccessor` for the `kavach-gemini-api-key` secret. See Google's [Workload Identity Federation guidance](https://github.com/google-github-actions/auth) and [Cloud Run secrets documentation](https://cloud.google.com/run/docs/configuring/services/secrets).

### Deploy

Open the repository's Actions tab, select **Deploy Kavach1930 to Google Cloud Run**, and click **Run workflow**. Keep `allow_unauthenticated` off by default. Enable public access only if a public judging URL is required and you have considered Gemini quota/cost abuse; an unauthenticated service is not a safe production deployment.

Cloud Run/Cloud Build may require an enabled billing account. Gemini API's no-cost quota (where available) does not make Google Cloud hosting universally free. Check current limits and pricing before deployment.

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
