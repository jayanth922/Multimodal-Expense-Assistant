from google import genai
from app.core.settings import settings

_client = genai.Client(api_key=settings.GOOGLE_API_KEY)

def ask_gemini(prompt: str) -> str:
    try:
        resp = _client.models.generate_content(
            model=settings.GENAI_MODEL,
            contents=prompt
        )
        return (getattr(resp, "text", None) or "").strip()
    except Exception as e:
        return f"Fallback failed: {e}"
