import os

from fastmcp.server.auth import AccessToken, TokenVerifier


def get_api_key() -> str:
    """Get API key from environment (for stdio/local transport)."""
    key = os.environ.get("PANTHER_API_KEY", "")
    if not key:
        raise RuntimeError(
            "PANTHER_API_KEY environment variable is not set. "
            "Get your API key at https://panther.watch and set it as: "
            "export PANTHER_API_KEY=pthr_..."
        )
    return key


class PantherTokenVerifier(TokenVerifier):
    """Accepts pthr_ API keys for the hosted MCP server.

    Format validation only — actual auth happens on the Django API side.
    """

    async def verify_token(self, token: str) -> AccessToken | None:
        if not token.startswith("pthr_"):
            return None
        return AccessToken(
            token=token,
            client_id=token[:20],
            scopes=[],
        )
