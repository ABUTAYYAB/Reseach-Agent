# 🔬 Autonomous AI Research Agent (Week 4 Internship Project)

A modular, extensible **Agentic AI Research Assistant** built in Python with **Groq LLM** (`openai/gpt-oss-120b`), live web search (`ddgs`), document analysis (`pypdf`), session memory, and lifecycle observability hooks.

---

## 🌟 Assignment Requirements Verification

| Requirement | Implementation Module | How it was Verified |
| :--- | :--- | :--- |
| **1. Web-Search Skill** | [`tools/search.py`](file:///home/malik/ai/projects/reserach-agent/tools/search.py) | Queries DuckDuckGo live web search for recent papers, news, and technical breakthroughs. |
| **2. Session Memory** | [`agent/memory.py`](file:///home/malik/ai/projects/reserach-agent/agent/memory.py) | Dual-tier memory: Conversation buffer + explicit fact store that retains user preferences and notes across turns. |
| **3. Lifecycle Hooks with Timestamps** | [`agent/hooks.py`](file:///home/malik/ai/projects/reserach-agent/agent/hooks.py) | Intercepts all tool calls (`before_tool_call`, `after_tool_call`, `on_tool_error`), records exact ISO 8601 timestamps and latency, and persists to `logs/tool_executions.log`. |
| **4. File-Read Plugin** | [`tools/file_reader.py`](file:///home/malik/ai/projects/reserach-agent/tools/file_reader.py) | Safely reads local files (`.txt`, `.md`, and `.pdf` documents) page-by-page. |
| **5. Multi-Hop Demo** | [`main.py`](file:///home/malik/ai/projects/reserach-agent/main.py) | Single agent resolves compound 3-hop research query combining document inspection, live web search, memory recall, and timestamped hooks. |

---

## 📂 Architecture & Directory Structure

```
reserach-agent/
├── agent/
│   ├── __init__.py          # Exports core classes
│   ├── core.py              # ReAct Agent loop (orchestration & function calling)
│   ├── memory.py            # Conversation buffer & semantic fact memory store
│   └── hooks.py             # Lifecycle hooks system & timestamp logger
├── tools/
│   ├── __init__.py          # Exports all tools and registry
│   ├── base.py              # BaseTool abstract class & ToolRegistry
│   ├── search.py            # Web search skill (DuckDuckGo via ddgs)
│   ├── file_reader.py       # File reader plugin (.txt, .md, .pdf)
│   └── memory_tool.py       # Remember & Recall memory tools
├── sample_data/
│   ├── quantum_research_brief.pdf  # Test PDF document with research specifications
│   └── internship_notes.txt        # Test text file
├── logs/
│   ├── tool_executions.log  # Human-readable audit log with ISO timestamps
│   └── tool_executions.jsonl# Machine-readable JSONL execution trace
├── .env                     # Your API keys (ignored by git)
├── .env.example             # Safe template
├── .gitignore               # Protects .env, .venv, and logs
├── requirements.txt         # Dependencies
├── plan.md                  # Comprehensive concept guide & roadmap
└── main.py                  # Entrypoint: Multi-hop demo & interactive CLI
```

---

## 🚀 How to Run

### 1. Run the Automated Multi-Hop Demo
Validates all 5 assignment requirements end-to-end:
```bash
.venv/bin/python main.py --demo
```

### 2. Run Interactive CLI Mode
Chat with the agent in real time, inspect files, and watch hooks log everything live:
```bash
.venv/bin/python main.py --interactive
```

---

## 🧠 Core Concepts Explained

### 1. The ReAct Agent Loop ([`agent/core.py`](file:///home/malik/ai/projects/reserach-agent/agent/core.py))
* The agent does not blindly output text. It runs in an iterative loop:
  $$\text{User Query} \longrightarrow \text{LLM Reasoning} \longrightarrow \text{Tool Selection} \longrightarrow \text{Hook Interception} \longrightarrow \text{Execution} \longrightarrow \text{Observation} \longrightarrow \text{Synthesis}$$
* If the LLM determines more data is needed, it triggers tools until it is ready to give a complete answer.

### 2. Lifecycle Hooks & Observability ([`agent/hooks.py`](file:///home/malik/ai/projects/reserach-agent/agent/hooks.py))
* `ToolExecutionLoggerHook` intercepts every execution step:
  - **Pre-Tool Hook**: Captures start timestamp $t_0$, tool name, and input arguments.
  - **Post-Tool Hook**: Captures end timestamp $t_1$, latency $(t_1 - t_0)$ in milliseconds, output character count, and success state.
  - **Persistent Logging**: Automatically writes to `logs/tool_executions.log` and `logs/tool_executions.jsonl`.

### 3. Session Memory ([`agent/memory.py`](file:///home/malik/ai/projects/reserach-agent/agent/memory.py))
* **Buffer Memory**: Tracks raw conversation turns.
* **Fact Memory**: When the user provides explicit preferences or constraints, the agent invokes `remember_fact` to persist them across the entire session.
