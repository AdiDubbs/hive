"""Runtime configuration for Meeting Prep Agent."""

from dataclasses import dataclass

from framework.config import RuntimeConfig

default_config = RuntimeConfig()


@dataclass
class AgentMetadata:
    name: str = "Meeting Prep Agent"
    version: str = "1.0.0"
    description: str = (
        "Researches meeting attendees and their company using web search, "
        "then generates a structured HTML briefing with profiles, recent news, "
        "tailored talking points, and suggested questions."
    )
    intro_message: str = (
        "Hi! I'm your meeting prep assistant. Tell me who you're meeting with "
        "and I'll research them, their company, and help you walk in prepared. "
        "What meeting would you like to prep for?"
    )


metadata = AgentMetadata()
