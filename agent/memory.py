"""
Session Memory System.
Requirement 2: Add memory: agent recalls facts from earlier in the session.
Provides short-term conversation buffering and an active semantic fact store.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


class FactItem:
    """Represents a discrete fact recalled by the agent across the session."""

    def __init__(self, key: str, fact: str, timestamp: Optional[str] = None):
        self.key = key
        self.fact = fact
        self.timestamp = timestamp or datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> Dict[str, str]:
        return {
            "key": self.key,
            "fact": self.fact,
            "timestamp": self.timestamp,
        }

    def __repr__(self) -> str:
        return f"FactItem(key='{self.key}', fact='{self.fact}')"


class SessionMemory:
    """
    Manages session context:
      1. Dialog Buffer: Full conversational message history.
      2. Fact Memory Store: Explicitly stored facts, user preferences, and intermediate conclusions.
    """

    def __init__(self):
        self.messages: List[Dict[str, Any]] = []
        self.facts: Dict[str, FactItem] = {}

    def add_message(
        self,
        role: str,
        content: Optional[str] = None,
        tool_calls: Optional[List[Dict[str, Any]]] = None,
        tool_call_id: Optional[str] = None,
        name: Optional[str] = None,
    ) -> None:
        """Appends a message to the conversation history."""
        msg: Dict[str, Any] = {"role": role}
        if content is not None:
            msg["content"] = content
        if tool_calls is not None:
            msg["tool_calls"] = tool_calls
        if tool_call_id is not None:
            msg["tool_call_id"] = tool_call_id
        if name is not None:
            msg["name"] = name
        self.messages.append(msg)

    def add_fact(self, key: str, fact: str) -> None:
        """
        Stores or updates a remembered fact in the session fact store.
        """
        clean_key = key.strip().lower()
        self.facts[clean_key] = FactItem(key=clean_key, fact=fact.strip())

    def get_facts(self) -> List[Dict[str, str]]:
        """Returns all remembered facts as a list of dictionaries."""
        return [f.to_dict() for f in self.facts.values()]

    def get_formatted_facts(self) -> str:
        """Formats remembered facts into a clean markdown block for LLM system context."""
        if not self.facts:
            return "No stored session facts yet."
        
        lines = ["### 🧠 Session Fact Memory (Recalled Facts):"]
        for key, item in self.facts.items():
            lines.append(f"- **{key.title()}**: {item.fact} (recorded: {item.timestamp})")
        return "\n".join(lines)

    def search_facts(self, query: str) -> List[FactItem]:
        """Simple keyword search across stored facts."""
        q = query.lower()
        return [
            f for key, f in self.facts.items()
            if q in key or q in f.fact.lower()
        ]

    def clear(self) -> None:
        """Clears memory for a fresh session."""
        self.messages.clear()
        self.facts.clear()
