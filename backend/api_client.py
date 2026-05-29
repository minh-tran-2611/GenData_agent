from typing import Any, Optional
import httpx

from models import EndpointConfig, BusinessConfig


def _resolve_url(business: BusinessConfig, endpoint: EndpointConfig) -> str:
    url = endpoint.url
    if url.startswith("http://") or url.startswith("https://"):
        return url
    base = business.base_url.rstrip("/")
    path = url if url.startswith("/") else "/" + url
    return f"{base}{path}" if base else url


def call_endpoint(
    business: BusinessConfig,
    endpoint: EndpointConfig,
    body: Optional[dict[str, Any]] = None,
    extra_params: Optional[dict[str, Any]] = None,
    timeout: float = 20.0,
) -> tuple[int, Any, Optional[str]]:
    """Call a configured endpoint. Returns (status_code, response_data, error_message)."""
    url = _resolve_url(business, endpoint)
    headers = dict(endpoint.headers or {})
    params = dict(endpoint.query_params or {})
    if extra_params:
        params.update(extra_params)
    try:
        with httpx.Client(timeout=timeout) as client:
            resp = client.request(
                endpoint.method,
                url,
                headers=headers,
                params=params or None,
                json=body if endpoint.method in ("POST", "PUT", "PATCH") else None,
            )
        ct = resp.headers.get("content-type", "")
        if "application/json" in ct:
            try:
                data = resp.json()
            except Exception:
                data = resp.text
        else:
            data = resp.text
        if resp.status_code >= 400:
            return resp.status_code, data, f"HTTP {resp.status_code}"
        return resp.status_code, data, None
    except httpx.RequestError as e:
        return 0, None, f"Request error: {e}"
    except Exception as e:
        return 0, None, f"Unexpected error: {e}"
