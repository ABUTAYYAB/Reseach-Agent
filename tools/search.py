"""
Web Search Skill.
Uses DuckDuckGo Search (via ddgs) to provide real-time web search capability.
"""

from typing import Any, Dict
from ddgs import DDGS
from tools.base import BaseTool


class WebSearchTool(BaseTool):
    """
    Skill for searching the live web.
    Requirement 1: Build a research agent with a web-search skill.
    """

    name: str = "web_search"
    description: str = (
        "Search the live web for up-to-date information, facts, research papers, "
        "and news. Use this whenever you need recent knowledge not in your training data "
        "or when verifying facts."
    )
    parameters: Dict[str, Any] = {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The search query keywords to search for on the web.",
            },
            "max_results": {
                "type": "integer",
                "description": "Maximum number of search results to return (default: 4, max: 6).",
                "default": 4,
            },
        },
        "required": ["query"],
    }

    def execute(self, query: str, max_results: int = 4) -> str:
        """
        Executes a web search and formats the results into clean text.
        """
        if not query or not query.strip():
            return "Error: Search query cannot be empty."

        max_results = min(max(1, int(max_results)), 6)

        try:
            ddgs = DDGS()
            raw_results = list(ddgs.text(query.strip(), max_results=max_results))

            if not raw_results:
                return f"No search results found for query: '{query}'"

            formatted_results = []
            for idx, item in enumerate(raw_results, 1):
                title = item.get("title", "No Title")
                snippet = item.get("body", "No Snippet")
                href = item.get("href", "")
                formatted_results.append(
                    f"[{idx}] {title}\n    Snippet: {snippet}\n    URL: {href}"
                )

            return "\n\n".join(formatted_results)

        except Exception as e:
            return f"Error executing web search for '{query}': {str(e)}"
