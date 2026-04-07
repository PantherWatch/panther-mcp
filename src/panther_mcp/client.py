import os
from typing import Any

import httpx

from .auth import get_api_key

DEFAULT_BASE_URL = "https://panther.watch/api/v1"


class PantherClient:
    def __init__(self, api_key: str | None = None):
        self.base_url = os.environ.get("PANTHER_API_URL", DEFAULT_BASE_URL).rstrip("/")
        self.api_key = api_key or get_api_key()
        self._client = httpx.Client(
            base_url=self.base_url,
            headers={"Authorization": f"Bearer {self.api_key}"},
            timeout=60.0,
        )

    def get(self, path: str, params: dict | None = None) -> Any:
        response = self._client.get(path, params=params)
        response.raise_for_status()
        return response.json()

    def post(self, path: str, json: dict | None = None) -> Any:
        response = self._client.post(path, json=json)
        response.raise_for_status()
        return response.json()
