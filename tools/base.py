"""
Base Tool module.
Defines the abstract BaseTool class and ToolRegistry for all agent tools and plugins.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class BaseTool(ABC):
    """
    Abstract Base Class for all tools/skills/plugins.
    Every tool must define:
      - name: Unique identifier for the LLM function call
      - description: Clear instruction telling the LLM WHEN and HOW to use this tool
      - parameters: JSON Schema defining the expected arguments
    """

    name: str = ""
    description: str = ""
    parameters: Dict[str, Any] = {}

    @abstractmethod
    def execute(self, **kwargs) -> str:
        """
        Executes the tool with the given arguments and returns a string response.
        """
        pass

    def to_openai_tool(self) -> Dict[str, Any]:
        """
        Converts the tool definition to standard OpenAI / Groq tool schema format.
        """
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
        }


class ToolRegistry:
    """
    Registry that manages available tools and dispatches calls to the right tool.
    """

    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}

    def register(self, tool: BaseTool) -> None:
        """Registers a new tool instance."""
        self._tools[tool.name] = tool

    def get(self, name: str) -> Optional[BaseTool]:
        """Retrieves a tool by name."""
        return self._tools.get(name)

    def list_tools(self) -> List[BaseTool]:
        """Returns all registered tool instances."""
        return list(self._tools.values())

    def get_tool_schemas(self) -> List[Dict[str, Any]]:
        """Returns OpenAI/Groq compatible JSON tool schemas for all registered tools."""
        return [tool.to_openai_tool() for tool in self._tools.values()]

    def execute(self, name: str, **kwargs) -> str:
        """Dispatches an execution request to the appropriate tool."""
        tool = self.get(name)
        if not tool:
            return f"Error: Tool '{name}' not found. Available tools: {list(self._tools.keys())}"
        try:
            return tool.execute(**kwargs)
        except Exception as e:
            return f"Error executing tool '{name}': {str(e)}"
