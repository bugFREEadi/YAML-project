# Declarative Multi-Agent Orchestration Using YAML - Hackathon Evaluation

## 1. Problem Statement Explanation

### What problem is this project solving?
This project solves the complexity of orchestrating multiple AI agents. Typically, building multi-agent systems requires writing complex Python code, managing state, handling API calls, and manually wiring together different agents. This makes it hard for non-experts to build agentic workflows and hard for developers to maintain them.

### Why are current approaches difficult?
- **High Code Complexity**: You have to write boilerplate code for every agent interaction.
- **Hard to Visualize**: It's difficult to see the "flow" of tasks just by looking at Python code.
- **Vendor Lock-in**: Many frameworks tightly couple you to a specific provider.
- **Debugging Nightmares**: Tracing where a multi-agent conversation went wrong is difficult without structured logging.

### How YAML-based orchestration helps
- **Declarative vs. Imperative**: You simply describe *what* you want (agents, roles, workflow) in a simple YAML file, and the engine handles the *how*.
- **Language Agnostic Design**: The logic is in YAML, making it portable and easy to understand.
- **Rapid Prototyping**: You can swap agents, change logic from sequential to parallel, or switch models by changing a few lines of text.

---

## 2. My Approach

### Overall Architecture
The system is built as a **modular orchestration engine**.
1.  **Input**: A YAML configuration file.
2.  **Validator**: Checks the YAML for errors and circular dependencies.
3.  **Executor**: The core engine that interprets the workflow graph.
4.  **Agent Runtimes**: Isolated execution environments for each agent (supporting OpenAI, Gemini, Anthropic).
5.  **Output Formatter**: Generates strict, structured output for easy consumption.

### How YAML is used
- **Agents**: Defined with `id`, `role`, `goal`, and `model`. You can also define `sub_agents` for hierarchy.
- **Workflow**: Defined in a `workflow` block. You specify `type` (sequential or parallel) and the flow using `steps` or `branches`.
- **Flow Control**: simple list for sequential, branches for parallel, and `then` for chaining.

### Step-by-Step Execution
1.  **Load & Validate**: The system reads the YAML and ensures it's valid.
2.  **Graph Construction**: It builds an in-memory graph of the workflow.
3.  **Execution Loop**:
    -   **Sequential**: Agents run one after another, passing context forward.
    -   **Parallel**: Agents run concurrently using threads, and their results are aggregated.
    -   **Context Passing**: The context (previous results) is accumulated and passed to the next agent.
4.  **Final Output**: The comprehensive log and final result are printed.

### Agent Interaction
- **Context Awareness**: Every agent receives a "Context" string containing the outputs of previous agents.
- **Sub-agents**: A lead agent can have sub-agents. The engine automatically executes sub-agents first and aggregates their results into the lead agent's context *before* the lead agent runs.

---

## 3. Files Explanation

### `run.py` (The Entry Point)
- **Purpose**: Main CLI entry point.
- **Function**: Handles arguments, invokes the validator, manages the global error handling, and calls the executor.
- **Why**: It isolates the CLI logic from the core business logic.

### `backend/validator.py` (The Guard)
- **Purpose**: Ensures the YAML is robust.
- **Function**: Checks for missing fields, correct types, valid workflow structures, and detects circular dependencies in agent calls.
- **Why**: Prevents runtime crashes by catching configuration errors early.

### `backend/executor.py` (The Engine)
- **Purpose**: The heart of the system.
- **Function**: Contains `run_agent` (handles individual agent execution, including sub-agents and tools) and `process_step` (recursively handles workflow nodes, parallel threads, and context passing).
- **Why**: It abstracts the complexity of how agents actually run.

### `backend/agent.py` (The Data Model)
- **Purpose**: Represents a single Agent.
- **Function**: A clean class to store agent attributes and a method `build_prompt` to mix static instructions with dynamic context.

### `backend/models/router.py` (The Model Gateway)
- **Purpose**: Universal model interface.
- **Function**: Takes a simple model name (e.g., "openai", "gemini") and routes it to the specific API client, handling API keys and errors.
- **Why**: Allows easy switching of models without code changes.

### `backend/output_formatter.py` (The Presenter)
- **Purpose**: Controls what the user sees.
- **Function**: Generates the 4 strict sections: Concept Diagram, Agent Responses, Reviewer Summary, and Call Trace.
- **Why**: Ensures the output is professional, readable, and structured.

---

## 4. Implementation Details

### How YAML is parsed
I use `PyYAML` to load the file into a Python dictionary. Immediate validation checks if the structure matches the schema (agents list, workflow dict).

### How API calls are made
The `router.py` uses specific SDKs (or REST calls) for OpenAI, Gemini, and Anthropic. All calls are wrapped in try/except blocks to provide friendly error messages (e.g., "API Key missing") instead of crashing.

### Sequential vs. Parallel
- **Sequential**: A simple loop iterates through the list of steps. The accumulated context string grows with each step.
- **Parallel**: Uses Python's `concurrent.futures.ThreadPoolExecutor`. Branches run in separate threads. The main thread waits for all to finish, collects results, joins them, and passes them to the `then` node.

### Error Handling
Every tool execution, model call, and logic step is wrapped in safety layers. If a tool times out or a model fails, the system catches it, logs a structured error object, and allows the workflow to fail gracefully or continue if non-critical.

### Output Generation
The `output_formatter.py` reads the global `EXECUTION_LOG`. This is crucial because it captures *every* interaction (including sub-agents and repeated calls) in chronological order, ensuring nothing is lost in the final report.

---

## 5. Results & Demo Flow

### Input
I provide a simple YAML file, for example, `samples/calculator.yaml`. It defines a "Mathematician" agent and a "Python Analyst" agent.

### Output
The system produces a beautiful terminal output with 4 sections:
1.  **Diagram**: Visual arrow-based flow (e.g., `math_expert --> python_analyst`).
2.  **Responses**: Detailed output from each agent.
3.  **Reviewer**: (If applicable) A consolidated summary.
4.  **Trace**: A table showing exactly which model was used and for what purpose.

### Why is this useful?
It turns complex AI orchestration into a "config-file" problem. Anyone can design a multi-agent system in minutes without writing a single line of Python.

### Differentiation
Unlike other complex frameworks (like LangChain or AutoGen) which require heavy coding, this is **Pure Configuration**. It's stricter, easier to visualize, and specifically designed for deterministic logical flows.

---

## 6. Judges Pitch (30-40 Seconds)

"Hi, I've built a **Declarative Multi-Agent Orchestration Engine**.

Problem: Building multi-agent systems today is too complex—it requires writing heavy, error-prone code just to chain two prompts together.

My Solution: I moved the complexity into a **YAML-based engine**. You essentially 'program' your agents in English and YAML. You define who they are, what tools they have (like calculators or Python), and how they connect—sequentially or in parallel.

Under the hood, my engine handles the heavy lifting: parallel threading, context aggregation, model routing (OpenAI/Gemini), and error safety.

The result? You can prototype a complex team of AI agents in 30 seconds just by writing a config file, with zero python code. It’s clean, visual, and stable."
