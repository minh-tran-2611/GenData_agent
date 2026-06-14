import sys
import google.auth
from anthropic import AnthropicVertex

# ADC: chạy `gcloud auth application-default login` trước (không cần JSON key).
creds, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
PROJECT = "project-b4b13663-816a-47bd-98c"

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
