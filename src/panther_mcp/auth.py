import os


def get_api_key() -> str:
    key = os.environ.get("PANTHER_API_KEY", "")
    if not key:
        raise RuntimeError(
            "PANTHER_API_KEY environment variable is not set. "
            "Get your API key at https://panther.watch and set it as: "
            "export PANTHER_API_KEY=pthr_..."
        )
    return key
