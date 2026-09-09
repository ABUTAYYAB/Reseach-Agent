"""
Memory Tools.
Enables the agent to explicitly store and retrieve facts in its long-term session memory.
"""

from typing import Any, Dict
from tools.base import BaseTool
from agent.memory import SessionMemory


class RememberFactTool(BaseTool):
    """
    Skill for saving facts to session memory.
    """

    name: str = "remember_fact"
    description: str = (
        "Store an important fact, user preference, or research finding into long-term session memory "
        "so you can recall it across multiple conversation turns."
    )
    parameters: Dict[str, Any] = {
        "type": "object",
        "properties": {
            "key": {
                "type": "string",
                "description": "Short category or topic name for the fact (e.g., 'user_name', 'project_deadline', 'topic_focus').",
            },
            "fact": {
                "type": "string",
                "description": "The detailed fact to remember.",
            },
        },
        "required": ["key", "fact"],
    }

    def __init__(self, memory: SessionMemory):
        self.memory = memory

    def execute(self, key: str, fact: str) -> str:
        self.memory.add_fact(key=key, fact=fact)
        return f"Successfully stored fact under key '{key}': {fact}"


class RecallFactsTool(BaseTool):
    """
    Skill for querying stored facts in session memory.
    """

    name: str = "recall_facts"
    description: str = (
        "Search or list all facts, user preferences, and research notes stored in session memory."
    )
    parameters: Dict[str, Any] = {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Optional search term to filter facts by. Leave empty to list all stored facts.",
                "default": "",
            }
        },
    }

    def __init__(self, memory: SessionMemory):
        self.memory = memory

    def execute(self, query: str = "") -> str:
        if not self.memory.facts:
            return "Session memory is currently empty. No facts have been stored yet."
        if not query or not query.strip():
            return self.memory.get_formatted_facts()
        matches = self.memory.search_facts(query)
        if not matches:
            return f"No facts found matching query '{query}'."
        return "Matching facts in session memory:\n" + "\n".join(
            [f"- [{f.key}]: {f.fact} (time: {f.timestamp})" for f in matches]
        )
