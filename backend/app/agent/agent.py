from google.adk.agents import LlmAgent as Agent
from app.services.adk_tools import (
    add_expense_tool, total_spend_tool, summary_by_category_tool, rag_search_tool
)

root_agent = Agent(
    model="gemini-2.5-flash",
    name="expense_assistant",
    description="Personal expense assistant that can add expenses, compute summaries, and consult internal guidance.",
    instruction=(
        "You are a helpful expense assistant.\n"
        "- When the user asks about supported categories, policies, or how-to, "
        "ALWAYS call rag_search_tool(query) first and base your answer on those results.\n"
        "- Supported categories come from our internal guide; list them as bullets.\n"
        "- For DB actions, prefer these tools when relevant:\n"
        "  • add_expense_tool(amount, date_str, vendor, category, currency='USD', notes=None)\n"
        "  • total_spend_tool(start=None, end=None, category=None)\n"
        "  • summary_by_category_tool(start=None, end=None)\n"
        "Use ISO dates (YYYY-MM-DD). Ask for missing fields before writing."
    ),
    tools=[
        add_expense_tool,
        total_spend_tool,
        summary_by_category_tool,
        rag_search_tool,
    ],
)
