"""
Standalone Groq connectivity test.

Usage:
    python test_groq_connection.py
"""
from openai import OpenAI

from backend.config import GROQ_API_KEY, GROQ_BASE_URL, GROQ_MODEL, validate_groq_config


def main() -> None:
    validate_groq_config()

    client = OpenAI(
        api_key=GROQ_API_KEY,
        base_url=GROQ_BASE_URL,
    )
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": "Return a short plain text response."},
            {"role": "user", "content": "Reply with the word connected."},
        ],
        temperature=0,
    )

    content = response.choices[0].message.content
    if not content or not content.strip():
        raise RuntimeError("Groq connectivity test failed: empty response content")

    print("Groq connectivity OK")
    print(f"Model: {GROQ_MODEL}")
    print(f"Endpoint: {GROQ_BASE_URL}")
    print(f"Response: {content.strip()}")


if __name__ == "__main__":
    main()
