import pytest

from panther_mcp.client import PantherClient


class TestPantherClient:
    def test_default_base_url(self, monkeypatch):
        monkeypatch.setenv("PANTHER_API_KEY", "pthr_testkey")
        monkeypatch.delenv("PANTHER_API_URL", raising=False)
        client = PantherClient()
        assert client.base_url == "https://panther.watch/api/v1"

    def test_custom_base_url(self, monkeypatch):
        monkeypatch.setenv("PANTHER_API_KEY", "pthr_testkey")
        monkeypatch.setenv("PANTHER_API_URL", "http://localhost:8000/api/v1")
        client = PantherClient()
        assert client.base_url == "http://localhost:8000/api/v1"

    def test_trailing_slash_stripped(self, monkeypatch):
        monkeypatch.setenv("PANTHER_API_KEY", "pthr_testkey")
        monkeypatch.setenv("PANTHER_API_URL", "http://localhost:8000/api/v1/")
        client = PantherClient()
        assert client.base_url == "http://localhost:8000/api/v1"

    def test_auth_header_set(self, monkeypatch):
        monkeypatch.setenv("PANTHER_API_KEY", "pthr_testkey")
        client = PantherClient()
        assert client._client.headers["authorization"] == "Bearer pthr_testkey"

    def test_raises_without_key(self, monkeypatch):
        monkeypatch.delenv("PANTHER_API_KEY", raising=False)
        with pytest.raises(RuntimeError):
            PantherClient()
