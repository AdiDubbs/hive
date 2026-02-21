"""
Meeting Prep Agent - Researches attendees and generates a structured briefing.

Given a meeting's attendees and agenda, searches the web to build profiles
for each person and their company, then delivers an HTML briefing with
talking points and suggested questions tailored to the meeting goal.
"""

from .agent import MeetingPrepAgent, default_agent, goal, nodes, edges
from .config import RuntimeConfig, AgentMetadata, default_config, metadata

__version__ = "1.0.0"

__all__ = [
    "MeetingPrepAgent",
    "default_agent",
    "goal",
    "nodes",
    "edges",
    "RuntimeConfig",
    "AgentMetadata",
    "default_config",
    "metadata",
]
