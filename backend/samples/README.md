# Sample YAML Files for Demo Testing

This directory contains **5 carefully curated sample files** that demonstrate the full capabilities of the YAML Agent Orchestration System.

---

## 📁 Sample Files Overview

### 1. **sequential.yaml** - Basic Sequential Workflow
**Purpose:** Simple sequential execution demo  
**Agents:** 2 (researcher → writer)  
**Workflow Type:** Sequential  
**Use Case:** Research and content creation pipeline

**What it demonstrates:**
- Basic sequential agent execution
- Context passing between agents
- Simple two-step workflow

**Run:**
```bash
python run.py samples/sequential.yaml
```

---

### 2. **parallel.yaml** - Parallel Execution with Aggregation
**Purpose:** Concurrent execution demo  
**Agents:** 3 (backend + frontend → reviewer)  
**Workflow Type:** Parallel → Sequential  
**Use Case:** Software design review process

**What it demonstrates:**
- Parallel agent execution (backend & frontend run simultaneously)
- Result aggregation (reviewer receives both outputs)
- Efficient concurrent processing

**Run:**
```bash
python run.py samples/parallel.yaml
```

---

### 3. **team.yaml** - Sub-Agents Hierarchy
**Purpose:** Hierarchical agent structure demo  
**Agents:** 3 (root with sub-agents: researcher & analyst)  
**Workflow Type:** Sequential with sub-agents  
**Use Case:** Product management with delegated research

**What it demonstrates:**
- Sub-agent architecture
- Hierarchical task delegation
- Context aggregation from multiple sub-agents
- Complex agent relationships

**Run:**
```bash
python run.py samples/team.yaml
```

---

### 4. **test.yaml** - Complex Multi-Stage Workflow
**Purpose:** Comprehensive production-like workflow  
**Agents:** 9 agents across 5 stages  
**Workflow Type:** Mixed (parallel + sequential)  
**Use Case:** Complete product launch planning

**What it demonstrates:**
- Multi-stage workflow execution
- Mixed parallel and sequential execution
- Complex agent orchestration
- Real-world production scenario
- Multiple aggregation points

**Stages:**
1. **Stage 1:** Parallel market research (3 agents)
2. **Stage 2:** Research synthesis (1 agent)
3. **Stage 3:** Parallel product development (3 agents)
4. **Stage 4:** Product integration (1 agent)
5. **Stage 5:** Launch planning (1 agent)

**Run:**
```bash
python run.py samples/test.yaml
```

---

### 5. **test_empty.yaml** - Error Handling Demo
**Purpose:** Robustness and error handling demonstration  
**Content:** Empty file (0 bytes)  
**Use Case:** Testing system resilience

**What it demonstrates:**
- Graceful error handling
- Detailed error messages
- Structured error output (output.json)
- System robustness
- User-friendly error reporting

**Run:**
```bash
python run.py samples/test_empty.yaml
```

**Expected Output:**
```
✗  File 'samples/test_empty.yaml' is empty
```

**Output JSON:**
```json
{
  "error": {
    "type": "empty_file",
    "message": "File 'samples/test_empty.yaml' is empty",
    "file": "samples/test_empty.yaml",
    "file_size": 0,
    "suggestion": "Provide a valid YAML configuration with agents and workflow sections"
  }
}
```

---

## 🎯 Recommended Demo Sequence

For a comprehensive demo, run the samples in this order:

1. **sequential.yaml** - Start with basics
2. **parallel.yaml** - Show concurrency
3. **team.yaml** - Demonstrate hierarchy
4. **test.yaml** - Show complex real-world scenario
5. **test_empty.yaml** - Prove robustness

---

## 🎨 Beautiful Terminal UI

All samples feature:
- ✨ **Gradient banners** with beautiful pastel colors
- 🎯 **Progress indicators** with real-time status
- 📊 **Structured output** with workflow diagrams
- 🔍 **LLM call traces** for transparency
- 💎 **Pastel color scheme** for easy reading

---

## 📝 Sample File Structure

Each valid YAML file follows this structure:

```yaml
agents:
  - id: agent_name
    role: Agent Role
    goal: What the agent should accomplish
    model: openai  # or gemini, claude
    # Optional fields:
    # sub_agents: [sub_agent_id]
    # toolsets: [python, web]
    # instruction: Detailed instructions

workflow:
  type: sequential  # or parallel
  # For sequential:
  steps:
    - agent: agent_id
  # For parallel:
  branches:
    - agent_id_1
    - agent_id_2
  then:
    agent: aggregator_id
```

---

## 🚀 Quick Start

```bash
# Navigate to backend directory
cd backend

# Run any sample
python run.py samples/sequential.yaml

# Or use default (startup.yaml if it exists)
python run.py
```

---

## 📊 Output Files

Each execution generates:
- **Terminal output** - Beautiful formatted results
- **output.json** - Structured JSON with all agent outputs
- **memory.json** - Agent memory and insights (if enabled)
- **audit.json** - Execution audit trail (if enabled)

---

## 🎓 Learning Path

1. **Beginners:** Start with `sequential.yaml`
2. **Intermediate:** Try `parallel.yaml` and `team.yaml`
3. **Advanced:** Run `test.yaml` for complex workflows
4. **Testing:** Use `test_empty.yaml` to see error handling

---

## 💡 Tips

- All samples use OpenAI by default (requires `OPENAI_API_KEY`)
- Modify `model:` field to use `gemini` or `claude`
- Check `output.json` for detailed execution results
- Use `test_empty.yaml` to verify error handling works
- Customize any sample by editing the YAML file

---

## 🔧 Troubleshooting

**Error: "OPENAI_API_KEY environment variable not set"**
- Set your API key in `.env` file or environment

**Error: "File not found"**
- Ensure you're in the `backend` directory
- Use correct path: `samples/filename.yaml`

**Empty output:**
- Check `output.json` for detailed error information
- Verify YAML syntax is correct

---

Enjoy exploring the YAML Agent Orchestration System! 🎉
