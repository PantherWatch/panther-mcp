import pytest

from panther_mcp.auth import get_api_key


class TestGetApiKey:
    def test_returns_key_when_set(self, monkeypatch):
        monkeypatch.setenv("PANTHER_API_KEY", "pthr_testkey123")
        assert get_api_key() == "pthr_testkey123"

    def test_raises_when_not_set(self, monkeypatch):
        monkeypatch.delenv("PANTHER_API_KEY", raising=False)
        with pytest.raises(RuntimeError, match="PANTHER_API_KEY"):
            get_api_key()

    def test_raises_when_empty(self, monkeypatch):
        monkeypatch.setenv("PANTHER_API_KEY", "")
        with pytest.raises(RuntimeError, match="PANTHER_API_KEY"):
            get_api_key()

    def test_error_message_includes_instructions(self, monkeypatch):
        monkeypatch.delenv("PANTHER_API_KEY", raising=False)
        with pytest.raises(RuntimeError, match="panther.watch"):
            get_api_key()
