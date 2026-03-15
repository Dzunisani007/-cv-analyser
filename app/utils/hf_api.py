from __future__ import annotations

import time
from typing import Any

import requests


def post_json_with_retry(
    *,
    url: str,
    headers: dict[str, str] | None,
    payload: dict[str, Any],
    timeout_seconds: int = 30,
    max_retries: int = 4,
    base_sleep_seconds: float = 1.0,
) -> requests.Response:
    """POST JSON with basic exponential backoff for transient HF errors.

    Retries:
    - 503 (model loading)
    - 429 (rate limiting)
    - timeouts / connection errors
    """

    last_exc: Exception | None = None
    for attempt in range(max_retries + 1):
        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=timeout_seconds)
            if resp.status_code in (429, 503):
                raise RuntimeError(f"retryable status={resp.status_code} body={resp.text[:200]}")
            resp.raise_for_status()
            return resp
        except Exception as e:  # noqa: BLE001
            last_exc = e
            if attempt >= max_retries:
                break
            sleep_s = base_sleep_seconds * (2**attempt)
            time.sleep(min(sleep_s, 10.0))

    if last_exc:
        raise last_exc
    raise RuntimeError("request failed")
