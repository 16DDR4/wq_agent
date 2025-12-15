# wq_client.py
from __future__ import annotations

import time
from typing import Any, Dict, Optional
import requests


class WQClient:
    """
    Minimal WorldQuant BRAIN client.
    Auth pattern (per your discovery):
      - Basic auth (session.auth = (username, password))
      - POST https://api.worldquantbrain.com/authentication
    Then reuse the same session for subsequent API calls.
    """

    def __init__(
        self,
        username: str,
        password: str,
        base_url: str = "https://api.worldquantbrain.com",
        timeout: float = 30.0,
        max_retries: int = 6,
        backoff_base: float = 0.8,
    ):
        self.username = username
        self.password = password
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries
        self.backoff_base = backoff_base

        self.session = requests.Session()
        self.session.auth = (self.username, self.password)

        self._authenticate()

    def _authenticate(self) -> None:
        url = f"{self.base_url}/authentication"
        r = self.session.post(url, timeout=self.timeout)
        # 401/403 => auth failed; raise to show exact reason
        r.raise_for_status()
        # 有些返回是 {"token":...} / {"user":...}，这里不强依赖结构
        # 只要 session 后续请求不 401 就算成功

    def get_json(self, url: str) -> Any:
        """
        GET a URL and return parsed JSON.
        Includes retry on transient errors and respects Retry-After if present.
        """
        return self._request_json("GET", url)

    def post_json(self, url: str, payload: Optional[Dict[str, Any]] = None) -> Any:
        return self._request_json("POST", url, json=payload)

    def _request_json(self, method: str, url: str, **kwargs) -> Any:
        # allow passing relative paths like "/users/self/alphas"
        if url.startswith("/"):
            url = f"{self.base_url}{url}"

        for attempt in range(1, self.max_retries + 1):
            resp = self.session.request(method, url, timeout=self.timeout, **kwargs)

            # handle rate limiting
            if resp.status_code in (429, 503) and "Retry-After" in resp.headers:
                try:
                    wait = float(resp.headers["Retry-After"])
                except ValueError:
                    wait = self.backoff_base * attempt
                time.sleep(wait)
                continue

            # transient server errors
            if resp.status_code >= 500:
                time.sleep(self.backoff_base * attempt)
                continue

            # auth expired: re-auth once and retry
            if resp.status_code in (401, 403):
                # try re-auth then retry
                if attempt == 1:
                    self._authenticate()
                    continue
                resp.raise_for_status()

            resp.raise_for_status()
            # Some endpoints may return empty body; guard
            if not resp.text.strip():
                return None
            return resp.json()

        raise RuntimeError(f"Request failed after retries: {method} {url}")
