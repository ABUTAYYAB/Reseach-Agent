"""
Lifecycle Hooks System.
Requirement 3: Implement a hook that logs every tool call with timestamps.
Provides pre/post execution interception, latency timing, and structured logging.
"""

import os
import json
from abc import ABC
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

console = Console()


class BaseHook(ABC):
    """
    Abstract interface for lifecycle hooks.
    Implement this class to observe or alter agent actions at runtime.
    """

    def on_tool_start(self, tool_name: str, tool_args: Dict[str, Any], timestamp: datetime) -> None:
        """Fires immediately before a tool begins execution."""
        pass

    def on_tool_end(
        self,
        tool_name: str,
        tool_args: Dict[str, Any],
        tool_output: str,
        duration_ms: float,
        timestamp: datetime,
    ) -> None:
        """Fires immediately after a tool finishes execution successfully."""
        pass

    def on_tool_error(
        self,
        tool_name: str,
        tool_args: Dict[str, Any],
        error: Exception,
        duration_ms: float,
        timestamp: datetime,
    ) -> None:
        """Fires if a tool encounters an unhandled exception."""
        pass


class ToolExecutionLoggerHook(BaseHook):
    """
    Concrete Hook that logs every tool call with exact ISO 8601 timestamps,
    execution latency (in milliseconds), arguments, and outcomes.
    
    Outputs to:
      1. Live Rich Terminal display (formatted with colors)
      2. Persistent Log File (logs/tool_executions.jsonl & logs/tool_executions.log)
    """

    def __init__(self, log_dir: str = "logs", verbose_console: bool = True):
        self.log_dir = log_dir
        self.verbose_console = verbose_console
        os.makedirs(self.log_dir, exist_ok=True)
        self.log_file = os.path.join(self.log_dir, "tool_executions.log")
        self.jsonl_file = os.path.join(self.log_dir, "tool_executions.jsonl")

    def _get_iso_timestamp(self, dt: Optional[datetime] = None) -> str:
        """Returns ISO 8601 formatted timestamp with timezone."""
        target_dt = dt or datetime.now(timezone.utc)
        return target_dt.isoformat()

    def on_tool_start(self, tool_name: str, tool_args: Dict[str, Any], timestamp: datetime) -> None:
        iso_time = self._get_iso_timestamp(timestamp)
        event = {
            "event": "TOOL_START",
            "timestamp": iso_time,
            "tool": tool_name,
            "arguments": tool_args,
        }

        self._write_to_files(event)

        if self.verbose_console:
            console.print(
                f"[bold cyan]🪝 [HOOK: PRE-TOOL][/bold cyan] "
                f"[dim]Timestamp: {iso_time}[/dim] | "
                f"Calling [bold yellow]{tool_name}[/bold yellow] with args: [italic]{json.dumps(tool_args)}[/italic]"
            )

    def on_tool_end(
        self,
        tool_name: str,
        tool_args: Dict[str, Any],
        tool_output: str,
        duration_ms: float,
        timestamp: datetime,
    ) -> None:
        iso_time = self._get_iso_timestamp(timestamp)
        # Snippet of output to prevent giant logs
        output_snippet = (
            tool_output[:300] + "..." if len(tool_output) > 300 else tool_output
        )

        event = {
            "event": "TOOL_END",
            "timestamp": iso_time,
            "tool": tool_name,
            "arguments": tool_args,
            "duration_ms": round(duration_ms, 2),
            "status": "SUCCESS",
            "output_length": len(tool_output),
            "output_snippet": output_snippet,
        }

        self._write_to_files(event)

        if self.verbose_console:
            console.print(
                f"[bold green]🪝 [HOOK: POST-TOOL][/bold green] "
                f"[dim]Timestamp: {iso_time}[/dim] | "
                f"Finished [bold yellow]{tool_name}[/bold yellow] in [bold magenta]{duration_ms:.1f}ms[/bold magenta] "
                f"([green]Success[/green], {len(tool_output)} chars returned)"
            )

    def on_tool_error(
        self,
        tool_name: str,
        tool_args: Dict[str, Any],
        error: Exception,
        duration_ms: float,
        timestamp: datetime,
    ) -> None:
        iso_time = self._get_iso_timestamp(timestamp)
        event = {
            "event": "TOOL_ERROR",
            "timestamp": iso_time,
            "tool": tool_name,
            "arguments": tool_args,
            "duration_ms": round(duration_ms, 2),
            "status": "ERROR",
            "error_message": str(error),
        }

        self._write_to_files(event)

        if self.verbose_console:
            console.print(
                f"[bold red]🪝 [HOOK: TOOL-ERROR][/bold red] "
                f"[dim]Timestamp: {iso_time}[/dim] | "
                f"Failed [bold yellow]{tool_name}[/bold yellow] after [bold magenta]{duration_ms:.1f}ms[/bold magenta] | "
                f"Error: [red]{str(error)}[/red]"
            )

    def _write_to_files(self, event: Dict[str, Any]) -> None:
        """Appends event log to persistent files."""
        # JSONL format for machine parsing
        with open(self.jsonl_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(event) + "\n")

        # Human readable text log
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(
                f"[{event['timestamp']}] [{event['event']}] Tool: {event['tool']} "
                f"| Data: {json.dumps(event, default=str)}\n"
            )


class HookManager:
    """
    Manages a collection of lifecycle hooks and broadcasts events to all of them.
    """

    def __init__(self, hooks: Optional[List[BaseHook]] = None):
        self.hooks: List[BaseHook] = hooks or []

    def register(self, hook: BaseHook) -> None:
        """Adds a hook to the manager."""
        self.hooks.append(hook)

    def trigger_tool_start(self, tool_name: str, tool_args: Dict[str, Any], timestamp: datetime) -> None:
        for hook in self.hooks:
            try:
                hook.on_tool_start(tool_name, tool_args, timestamp)
            except Exception as e:
                console.print(f"[red]Hook error in on_tool_start: {e}[/red]")

    def trigger_tool_end(
        self,
        tool_name: str,
        tool_args: Dict[str, Any],
        tool_output: str,
        duration_ms: float,
        timestamp: datetime,
    ) -> None:
        for hook in self.hooks:
            try:
                hook.on_tool_end(tool_name, tool_args, tool_output, duration_ms, timestamp)
            except Exception as e:
                console.print(f"[red]Hook error in on_tool_end: {e}[/red]")

    def trigger_tool_error(
        self,
        tool_name: str,
        tool_args: Dict[str, Any],
        error: Exception,
        duration_ms: float,
        timestamp: datetime,
    ) -> None:
        for hook in self.hooks:
            try:
                hook.on_tool_error(tool_name, tool_args, error, duration_ms, timestamp)
            except Exception as e:
                console.print(f"[red]Hook error in on_tool_error: {e}[/red]")
