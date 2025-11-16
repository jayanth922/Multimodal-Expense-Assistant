from dotenv import load_dotenv
load_dotenv()

import os
from app.core.settings import settings
os.environ.setdefault("GOOGLE_API_KEY", settings.GOOGLE_API_KEY)
os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "False")

from google.adk.runners import Runner
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.adk.agents.run_config import RunConfig
from app.agent.agent import root_agent

# NEW: import Content/Part to build a proper message
from google.genai.types import Content, Part

APP_NAME = "MultimodalExpenseAgent"
_session_service = InMemorySessionService()
_runner = Runner(app_name=APP_NAME, agent=root_agent, session_service=_session_service)

# ---- Compat helpers: handle multiple ADK signatures & None returns ----
async def _get_session_compat(session_id: str, user_id: str):
    try:
        # Newer ADK
        return await _session_service.get_session(app_name=APP_NAME, user_id=user_id, session_id=session_id)
    except TypeError:
        # Older ADK takes only session_id or (app_name, user_id, session_id) positional
        try:
            return await _session_service.get_session(session_id)
        except TypeError:
            return await _session_service.create_session(APP_NAME, user_id, session_id)

async def _create_session_compat(session_id: str, user_id: str):
    try:
        return await _session_service.create_session(app_name=APP_NAME, user_id=user_id, session_id=session_id)
    except TypeError:
        try:
            return await _session_service.create_session(APP_NAME, user_id, session_id)
        except TypeError:
            # Some very old builds accept only session_id
            return await _session_service.create_session(session_id)

async def ensure_session(session_id: str, user_id: str | None = None):
    user_id = user_id or session_id
    sess = await _get_session_compat(session_id, user_id)
    if sess is None:
        sess = await _create_session_compat(session_id, user_id)
    return sess

# NEW: helper to normalize messages
def _mk_part(text: str) -> Part:
    # Handle different genai builds
    try:
        # Preferred in newer builds
        return Part.from_text(text=text)  # keyword arg only
    except TypeError:
        # Fallback for older builds
        return Part(text=text)

def _to_content(message) -> Content:
    if isinstance(message, Content):
        return message
    return Content(role="user", parts=[_mk_part(str(message))])

async def run_agent(session_id: str, message_content):
    session = await ensure_session(session_id)
    rc = RunConfig(response_modalities=["TEXT"])

    events = []
    # Pass Content, not str
    content = _to_content(message_content)
    async for e in _runner.run_async(
        user_id=session.user_id,
        session_id=session.id,
        new_message=content,
        run_config=rc,
    ):
        events.append(e)
    return events
