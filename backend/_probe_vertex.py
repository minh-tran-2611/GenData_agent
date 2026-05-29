import sys
from google.oauth2 import service_account
from anthropic import AnthropicVertex

SCOPES = ["https://www.googleapis.com/auth/cloud-platform"]
creds = service_account.Credentials.from_service_account_file("vertex-sa.json", scopes=SCOPES)
PROJECT = "smiling-foundry-477815-s7"

regions = ["us-east5", "us-central1", "europe-west1", "asia-southeast1", "global"]
models = [
    "claude-sonnet-4-5@20250929",
    "claude-sonnet-4@20250514",
    "claude-3-7-sonnet@20250219",
    "claude-3-5-sonnet-v2@20241022",
    "claude-opus-4-1@20250805",
]

for region in regions:
    if region == "global":
        base_url = "https://aiplatform.googleapis.com/v1"
    else:
        base_url = f"https://{region}-aiplatform.googleapis.com/v1"
    client = AnthropicVertex(region=region, project_id=PROJECT, credentials=creds, base_url=base_url)
    for model in models:
        try:
            msg = client.messages.create(
                model=model,
                max_tokens=16,
                messages=[{"role": "user", "content": "say OK"}],
            )
            txt = "".join(b.text for b in msg.content if getattr(b, "type", None) == "text")
            print(f"SUCCESS region={region} model={model} -> {txt!r}")
        except Exception as e:
            msg = str(e).replace("\n", " ")[:160]
            print(f"FAIL    region={region} model={model} -> {type(e).__name__}: {msg}")
