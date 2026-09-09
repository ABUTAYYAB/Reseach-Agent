# 🔬 Autonomous AI Research Agent

A modular, extensible **Agentic AI Research Assistant** built in Python with **Groq LLM** (`openai/gpt-oss-120b`), live web search (`ddgs`), document analysis (`pypdf`), session memory, and lifecycle observability hooks.

Built as an end-to-end learning project to explore and demonstrate the foundational building blocks of autonomous AI systems from scratch.

---

## 🌟 Key Capabilities & Architecture

| Feature | Implementation | Description |
| :--- | :--- | :--- |
| **🌐 Live Web Search** | [`tools/search.py`](file:///home/malik/ai/projects/reserach-agent/tools/search.py) | Real-time web retrieval via DuckDuckGo (`ddgs`) with zero-config, no-API-key web queries. |
| **🧠 Session Memory** | [`agent/memory.py`](file:///home/malik/ai/projects/reserach-agent/agent/memory.py) | Dual-layer memory system: short-term conversation buffer + semantic fact store for cross-turn recall. |
| **🪝 Lifecycle Hooks** | [`agent/hooks.py`](file:///home/malik/ai/projects/reserach-agent/agent/hooks.py) | Intercepts pre/post tool calls, records exact ISO 8601 timestamps, latency in milliseconds, and persists audit logs. |
| **📄 Document Reader** | [`tools/file_reader.py`](file:///home/malik/ai/projects/reserach-agent/tools/file_reader.py) | Plugin for extracting structured text from local `.txt`, `.md`, and `.pdf` files. |
| **🔗 Multi-Hop Reasoning** | [`agent/core.py`](file:///home/malik/ai/projects/reserach-agent/agent/core.py) | ReAct reasoning loop resolving compound multi-step queries by chaining tools, documents, and memory. |

---

## 📂 Project Structure

```
reserach-agent/
├── agent/
│   ├── __init__.py          # Agent package exports
│   ├── core.py              # ReAct Agent loop (orchestration & function calling)
│   ├── memory.py            # Conversation buffer & semantic fact memory store
│   └── hooks.py             # Lifecycle hooks system & timestamp logger
├── tools/
│   ├── __init__.py          # Tool registry & exports
│   ├── base.py              # BaseTool abstract interface & ToolRegistry
│   ├── search.py            # Web search skill (DuckDuckGo via ddgs)
│   ├── file_reader.py       # File reader plugin (.txt, .md, .pdf)
│   └── memory_tool.py       # Remember & Recall memory tools
├── sample_data/
│   ├── quantum_research_brief.pdf  # Sample research brief for document parsing
│   └── project_notes.txt           # Sample text notes
├── logs/
│   ├── tool_executions.log  # Human-readable audit log with ISO timestamps
│   └── tool_executions.jsonl# Machine-readable JSONL execution trace
├── .env.example             # Environment variable template
├── .gitignore               # Protects .env, .venv, and logs
├── requirements.txt         # Project dependencies
├── plan.md                  # Comprehensive architectural deep dive & roadmap
├── requirements.md          # Technical specifications
└── main.py                  # Entrypoint: Multi-hop demo & interactive CLI
```

---

## 🚀 Quickstart Guide

### 1. Prerequisites
- Python 3.10+
- A free [Groq API Key](https://console.groq.com/) (or Google Gemini API Key)

### 2. Setup Environment
```bash
# Clone the repository
git clone https://github.com/ABUTAYYAB/Reseach-Agent.git
cd Reseach-Agent

# Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure API Keys
Create a `.env` file in the root directory:
```env
GROQ_API_KEY=gsk_your_groq_api_key_here
```

---

## 🎮 Running the Agent

### 1. Automated Multi-Hop Demo
Runs a multi-turn scenario validating file reading, live web search, memory recall, and timestamped hooks:
```bash
python main.py --demo
```

### 2. Interactive CLI Mode
Chat with the agent interactively, query files, search the web, and observe real-time hook logs:
```bash
python main.py --interactive
```

---

## 🧠 Deep Dive: Core Concepts

### 1. The ReAct Agent Loop ([`agent/core.py`](file:///home/malik/ai/projects/reserach-agent/agent/core.py))
The agent implements the ReAct (Reason + Act) loop:
$$\text{User Query} \longrightarrow \text{Reasoning} \longrightarrow \text{Tool Selection} \longrightarrow \text{Hook Interception} \longrightarrow \text{Execution} \longrightarrow \text{Observation} \longrightarrow \text{Synthesis}$$

### 2. Lifecycle Observability Hooks ([`agent/hooks.py`](file:///home/malik/ai/projects/reserach-agent/agent/hooks.py))
`ToolExecutionLoggerHook` intercepts every tool execution:
* **Pre-Tool Hook**: Captures start timestamp $t_0$, tool name, and input arguments.
* **Post-Tool Hook**: Captures end timestamp $t_1$, latency $(t_1 - t_0)$ in milliseconds, output size, and success status.
* **Persistent Logging**: Automatically writes to `logs/tool_executions.log` and `logs/tool_executions.jsonl`.

### 3. Session Memory System ([`agent/memory.py`](file:///home/malik/ai/projects/reserach-agent/agent/memory.py))
* **Buffer Memory**: Tracks dialogue turns for short-term conversational context.
* **Fact Store**: Persists extracted facts and user preferences across conversation turns via `remember_fact` and `recall_facts`.

---

## 📄 License
MIT License. Free for educational, research, and personal use.
