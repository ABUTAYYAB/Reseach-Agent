"""
Core ReAct Agent Engine.
Orchestrates LLM interaction, tool calling loops, lifecycle hooks, and session memory.
"""

import os
import json
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

from groq import Groq
from agent.memory import SessionMemory
from agent.hooks import HookManager, ToolExecutionLoggerHook
from tools.base import ToolRegistry

console = Console()

DEFAULT_SYSTEM_PROMPT = """You are an expert, meticulous Agentic AI Research Assistant.
Your goal is to answer research and multi-hop queries thoroughly and accurately.

You have access to the following tools:
1. `web_search`: Search the live web for papers, articles, and current facts.
2. `read_file`: Inspect local files (.txt, .md, .pdf) to read project documents or specs.
3. `remember_fact` / `recall_facts`: Manage explicit session memory for user preferences and facts.

Operational Rules:
- When answering multi-hop or multi-step questions:
  1. If local files need to be inspected, call `read_file`.
  2. If external facts or live breakthroughs are needed, call `web_search` with 1-2 targeted queries.
  3. Recall previous facts and preferences stated earlier in the session.
  4. Once you have gathered sufficient information, synthesize a complete, cohesive answer directly in your next response. Do NOT make redundant or repetitive tool calls.
- Always explicitly cite your sources (e.g. document filename, search result URLs, or session memory).
"""


class ResearchAgent:
    """
    Modular Agent that implements the ReAct loop:
      Reason -> Decide Tool -> Execute with Lifecycle Hooks -> Observe -> Synthesize Final Answer.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "openai/gpt-oss-120b",
        system_prompt: str = DEFAULT_SYSTEM_PROMPT,
        tool_registry: Optional[ToolRegistry] = None,
        memory: Optional[SessionMemory] = None,
        hook_manager: Optional[HookManager] = None,
        max_turns: int = 6,
        max_tokens: int = 800,
    ):
        self.api_key = api_key or os.environ.get("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError(
                "GROQ_API_KEY not found. Please set it in your .env file or pass it to ResearchAgent."
            )

        self.client = Groq(api_key=self.api_key)
        self.model = model
        self.system_prompt = system_prompt
        self.max_turns = max_turns
        self.max_tokens = max_tokens

        # Initialize Subsystems
        self.memory = memory or SessionMemory()
        self.tool_registry = tool_registry or ToolRegistry()
        self.hook_manager = hook_manager or HookManager([ToolExecutionLoggerHook()])

    def _call_llm_with_retry(
        self,
        messages_payload: List[Dict[str, Any]],
        tool_schemas: Optional[List[Dict[str, Any]]] = None,
    ):
        """Calls Groq with automatic retry on transient rate limits."""
        for attempt in range(4):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages_payload,
                    tools=tool_schemas if tool_schemas else None,
                    tool_choice="auto" if tool_schemas else None,
                    max_tokens=self.max_tokens,
                    temperature=0.2,
                )
                return response
            except Exception as e:
                err_str = str(e).lower()
                if "rate_limit" in err_str or "429" in err_str:
                    wait_time = (attempt + 1) * 2
                    console.print(
                        f"[yellow]⚠️ Rate limit encountered. Waiting {wait_time}s before retry...[/yellow]"
                    )
                    time.sleep(wait_time)
                else:
                    raise e
        raise RuntimeError("Max retries exceeded for LLM call.")

    def chat(self, user_message: str) -> str:
        """
        Processes a single user prompt through the multi-turn ReAct loop.
        """
        # 1. Add user message to conversation memory
        self.memory.add_message(role="user", content=user_message)

        # 2. Prepare dynamic system prompt with injected session facts
        current_facts = self.memory.get_formatted_facts()
        full_system_prompt = (
            f"{self.system_prompt}\n\n"
            f"{current_facts}\n\n"
            f"Current timestamp: {datetime.now(timezone.utc).isoformat()}"
        )

        turn_count = 0

        while turn_count < self.max_turns:
            turn_count += 1

            # Build messages list starting with the updated system prompt
            messages_payload = [{"role": "system", "content": full_system_prompt}]
            messages_payload.extend(self.memory.messages)

            # Get available tool schemas
            tool_schemas = self.tool_registry.get_tool_schemas()

            # Call LLM with retry support
            response = self._call_llm_with_retry(messages_payload, tool_schemas)

            choice = response.choices[0]
            message = choice.message

            # Case A: LLM decided to execute Tool Calls
            if message.tool_calls:
                # Append assistant tool call request to memory
                serialized_tool_calls = [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments,
                        },
                    }
                    for tc in message.tool_calls
                ]
                self.memory.add_message(
                    role="assistant",
                    content=message.content or "",
                    tool_calls=serialized_tool_calls,
                )

                # Process each tool call
                for tc in message.tool_calls:
                    tool_name = tc.function.name
                    raw_args = tc.function.arguments

                    try:
                        parsed_args = (
                            json.loads(raw_args) if isinstance(raw_args, str) else raw_args
                        )
                    except json.JSONDecodeError:
                        parsed_args = {"raw_input": raw_args}

                    # Trigger Pre-Tool Hook
                    start_time = datetime.now(timezone.utc)
                    t0 = time.perf_counter()
                    self.hook_manager.trigger_tool_start(
                        tool_name=tool_name,
                        tool_args=parsed_args,
                        timestamp=start_time,
                    )

                    # Execute the Tool
                    try:
                        tool_result = self.tool_registry.execute(tool_name, **parsed_args)
                        t1 = time.perf_counter()
                        duration_ms = (t1 - t0) * 1000.0
                        end_time = datetime.now(timezone.utc)

                        # Trigger Post-Tool Hook
                        self.hook_manager.trigger_tool_end(
                            tool_name=tool_name,
                            tool_args=parsed_args,
                            tool_output=tool_result,
                            duration_ms=duration_ms,
                            timestamp=end_time,
                        )
                    except Exception as err:
                        t1 = time.perf_counter()
                        duration_ms = (t1 - t0) * 1000.0
                        end_time = datetime.now(timezone.utc)
                        tool_result = f"Error during tool execution: {str(err)}"

                        # Trigger Tool-Error Hook
                        self.hook_manager.trigger_tool_error(
                            tool_name=tool_name,
                            tool_args=parsed_args,
                            error=err,
                            duration_ms=duration_ms,
                            timestamp=end_time,
                        )

                    # Append tool result to memory
                    self.memory.add_message(
                        role="tool",
                        content=tool_result,
                        tool_call_id=tc.id,
                        name=tool_name,
                    )

                # Continue the ReAct loop so the LLM can interpret tool output
                continue

            # Case B: LLM provided final answer text
            final_content = message.content or ""
            self.memory.add_message(role="assistant", content=final_content)
            return final_content

        return "Agent reached maximum reasoning turns limit without concluding."
