# 🚀 Declarative Multi-Agent Orchestration using YAML

> **A Pure Configuration approach to building complex AI Agent workflows.**
> _Build, Orchestrate, and Deploy AI Agents without writing a single line of Python code._

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.10+-yellow.svg)
![Agentic](https://img.shields.io/badge/status-Agentic-purple.svg)

---

## 🌟 Why this project?

Building multi-agent systems is **hard**. It typically involves:
-   Complex Python boilerplate.
-   Managing state & memory manually.
-   Writing extensive glue code for API calls.
-   Debugging "invisible" interactions.

**This engine changes that.** You define your entire agent team, their tools, and their workflow in a simple **YAML file**. The engine handles the rest—parallel execution, context passing, tool usage (ReAct), and error handling.

---

## ✨ Key Features

-   **📝 Declarative Config**: Define agents, roles, and flows in readable YAML.
-   **⚡ Hybrid Workflows**: Support for **Sequential** (Chain) and **Parallel** (Fan-out/Fan-in) architectures.
-   **🛠️ ReAct Agent Loop**: Agents can autonomously use tools (e.g., **Calculator**, **Python**) with a reasoning loop.
-   **🎨 Beautiful Terminal UI**: professionally designed **Pastel UI** with real-time spinners, tables, and borders.
-   **🧠 Smart Context**: Automatic context aggregation and memory management between agents.
-   **🛡️ Robust Error Handling**: Graceful failures with detailed error logs—system never crashes blindly.
-   **🔌 Model Agnostic**: Supports **OpenAI**, **Gemini**, and **Claude** (Anthropic) via a unified router.

---

## 🚀 Getting Started

### Prerequisites

-   Python 3.10 or higher
-   API Keys for your preferred models (OpenAI, Google, or Anthropic)

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/yourusername/yaml-agent-system.git
    cd yaml-agent-system
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    *(If specific requirements aren't listed, install: `pyyaml`, `openai`, `anthropic`, `google-generativeai`)*

3.  **Set Environment Variables:**
    Create a `.env` file or export your keys:
    ```bash
    export OPENAI_API_KEY="sk-..."
    # Optional
    export GOOGLE_API_KEY="AIza..."
    export ANTHROPIC_API_KEY="sk-ant..."
    ```

---

## 🏃‍♂️ Usage

Run any agent configuration by passing the YAML file to the `run.py` script.

### 1. Basic Sequential Flow
Run a researcher followed by a writer:
```bash
python3 backend/run.py backend/samples/sequential.yaml
```

### 2. Advanced Tool Usage (Calculator)
Run a Mathematician agent that can perform actual calculations using Python:
```bash
python3 backend/run.py backend/samples/calculator.yaml
```
_Watch as the agent triggers `CALCULATE:`, the system computes it, and returns the accurate result!_

---

## 📂 Project Structure

```text
.
├── backend/
│   ├── run.py                # 🏁 Entry Point
│   ├── executor.py           # ⚙️ Core Engine (ReAct Loop)
│   ├── agent.py              # 🤖 Agent Class Helper
│   ├── output_formatter.py   # 🎨 UI & Report Generator
│   ├── ui.py                 # 🌈 Pastel UI Library
│   ├── validator.py          # ✅ YAML Schema Validator
│   ├── mcp_tools.py          # 🛠️ Tool Implementations
│   ├── safety.py             # 🛡️ Error & Safety Utils
│   └── samples/              # 📂 Example YAML configs
└── output.json               # 💾 Last run's structured output
```

---

## 📝 Configuration Rules (YAML)

A typical configuration looks like this:

```yaml
agents:
  - id: math_expert
    role: Mathematician
    goal: Perform complex calculations reliably.
    toolsets: [calculator]  # Enable tools here

workflow:
  type: sequential
  steps:
    - agent: math_expert
    - agent: summary_writer
```

---

## 📸 Output Demo

The system generates a **Strict 4-Section Report** for every run:
1.  **Conceptual Workflow Diagram** (Visual Flowchart)
2.  **Detailed Agent Responses** (What they actually said/did)
3.  **Consolidated Reviewer Response** (Final summary)
4.  **LLM Call Trace Table** (Audit log of every API call & Tool use)

---

## 🏆 Hackathon Notes

This project demonstrates **"Agentic AI"** by moving beyond simple prompt chaining.
-   **Autonomy**: Agents decide *when* to use tools.
-   **Reliability**: Logic is maintained in code (`executor.py`), not just prompts.
-   **UX**: Built for developers who need visibility into "Black Box" AI systems.

---

_Built with ❤️ for the Hackathon._

