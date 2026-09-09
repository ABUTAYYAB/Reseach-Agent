"""
File Reader Plugin.
Allows the agent to read and extract text from local files, specifically .txt, .md, and .pdf documents.
"""

import os
from typing import Any, Dict
from pypdf import PdfReader
from tools.base import BaseTool


class FileReaderTool(BaseTool):
    """
    Plugin for reading local document files.
    Requirement 4: Add a file-read plugin: agent can read .txt / .pdf files.
    """

    name: str = "read_file"
    description: str = (
        "Read the contents of a local file. Supports plain text files (.txt, .md, .json) "
        "and PDF documents (.pdf). Use this to inspect local project briefs, specs, and documents."
    )
    parameters: Dict[str, Any] = {
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "The path to the local file (relative or absolute).",
            },
            "max_characters": {
                "type": "integer",
                "description": "Optional limit on characters to read (default: 4000).",
                "default": 4000,
            },
        },
        "required": ["file_path"],
    }

    def execute(self, file_path: str, max_characters: int = 4000) -> str:
        """
        Reads and extracts text from .txt, .md, or .pdf files.
        """
        if not file_path or not file_path.strip():
            return "Error: file_path must be provided."

        clean_path = file_path.strip()

        if not os.path.exists(clean_path):
            return f"Error: File not found at path '{clean_path}'."

        if not os.path.isfile(clean_path):
            return f"Error: Path '{clean_path}' is not a regular file."

        _, ext = os.path.splitext(clean_path.lower())

        try:
            if ext == ".pdf":
                return self._read_pdf(clean_path, max_characters)
            else:
                return self._read_text(clean_path, max_characters)
        except Exception as e:
            return f"Error reading file '{clean_path}': {str(e)}"

    def _read_pdf(self, path: str, max_chars: int) -> str:
        """Extracts text page-by-page from a PDF file."""
        reader = PdfReader(path)
        num_pages = len(reader.pages)
        extracted_text = [f"=== PDF Document: {os.path.basename(path)} ({num_pages} pages) ==="]

        total_length = 0
        for page_idx, page in enumerate(reader.pages, 1):
            text = page.extract_text() or ""
            page_content = f"\n--- Page {page_idx} ---\n{text.strip()}"
            extracted_text.append(page_content)
            total_length += len(page_content)
            if total_length >= max_chars:
                extracted_text.append(
                    f"\n[Note: Output truncated at {max_chars} characters. Total pages in PDF: {num_pages}]"
                )
                break

        return "\n".join(extracted_text)

    def _read_text(self, path: str, max_chars: int) -> str:
        """Reads plain text / markdown files."""
        # Try UTF-8 first, fallback to latin-1
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read(max_chars + 1)
        except UnicodeDecodeError:
            with open(path, "r", encoding="latin-1") as f:
                content = f.read(max_chars + 1)

        truncated = len(content) > max_chars
        content = content[:max_chars]

        result = f"=== File: {os.path.basename(path)} ===\n{content}"
        if truncated:
            result += f"\n\n[Note: Content truncated to {max_chars} characters]"
        return result
