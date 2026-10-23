"""Smoke-test the configured Gemini API connection."""

import os
import sys

from dotenv import load_dotenv
from google import genai


def main() -> int:
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    model = os.getenv("GEMINI_MODEL", "gemini-3.8-flash").strip()

    if not api_key or api_key == "replace_with_your_key":
        print("Missing GEMINI_API_KEY. Copy .env.example to .env and add your key.")
        return 2

    client = None
    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model=model,
            contents="Reply with exactly: KAVACH1930 API CONNECTION OK",
        )
        print("Gemini connection successful.")
        print(f"Model configured: {model}")
        print(f"Response: {response.text}")
        return 0
    except Exception as exc:
        print("Gemini connection failed.")
        print(f"Error type: {type(exc).__name__}")
        print(str(exc))
        return 1
    finally:
        if client is not None:
            client.close()


if __name__ == "__main__":
    sys.exit(main())
