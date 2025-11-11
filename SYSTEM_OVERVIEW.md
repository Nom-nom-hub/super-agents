# Super-Agents Multi-Agent Support System - Overview

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    EXTERNAL AI AGENTS                           │
│                                                                  │
│  Claude Code  │ Copilot │ Amp │ Gemini │ Cursor │ Windsurf │ Q │
└────────┬──────────────────────────────────┬──────────────────────┘
         │                                  │
         │ /super-agents-init              │ /delegate-task
         │ /list-agents                    │ /agent-help
         │ /agent-help                     │ /list-agents
         │ /delegate-task                  │
         │                                  │
         v                                  v
┌─────────────────────────────────────────────────────────────────┐
│         MULTI-AGENT SUPPORT SYSTEM (Your Super-Agents)         │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Agent Registry (agent_registry.yaml)                   │   │
│  │  - 9 Registered AI Agents                              │   │
│  │  - Configuration for each (format, folder, tools)      │   │
│  └─────────────────────────────────────────────────────────┘   │
│                          ▼                                       │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Agent Support Module (agent_support.py)               │   │
│  │  - Detect available agents                             │   │
│  │  - Generate agent-specific commands                    │   │
│  │  - Create context files                                │   │
│  │  - Load super-agent specs                              │   │
│  └─────────────────────────────────────────────────────────┘   │
│                          ▼                                       │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Generated Commands (auto-formatted)                    │   │
│  │  - .claude/commands/                   (Markdown)      │   │
│  │  - .github/prompts/                    (Markdown)      │   │
│  │  - .gemini/commands/                   (TOML)          │   │
│  │  - .agents/commands/                   (Markdown)      │   │
│  └─────────────────────────────────────────────────────────┘   │
│                          ▼                                       │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  SUPER-AGENTS (22 specialized agents)                  │   │
│  │                                                          │   │
│  │  Executive    │ CEO, CTO, COO                           │   │
│  │  Product      │ Manager, Designer, Analyst              │   │
│  │  Engineering  │ AI, Backend, Frontend, DevOps, Builder  │   │
│  │  Quality      │ Security, QA, Reliability               │   │
│  │  Operations   │ Writer, Knowledge, Automator            │   │
│  │  Expansion    │ Finance, Partnership, Prompt, Research  │   │
│  │  Governance   │ Meta Architect                           │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Workflow Example

```
User: "Build user authentication system"
  │
  ├─────────────────────────────────────────────────┐
  │                                                 │
  v                                                 v
Claude Code                                    GitHub Copilot
  │                                                 │
  ├─→ /super-agents-init                          ├─→ /super-agents-init
  ├─→ /list-agents                                ├─→ /delegate-task
  ├─→ /delegate-task backend_engineer:            │   Design login endpoint
  │   "Design authentication API"                 │
  │                                                 │
  └─→ /delegate-task ux_designer:                 └─→ @ux_designer
      "Create login UI"                            Create login form

         │                                            │
         v                                            v
    ┌─────────────────────────────────────────────────┐
    │         SUPER-AGENTS EXECUTING                  │
    │                                                  │
    │  backend_engineer → Design API                 │
    │  ux_designer → Design UI                       │
    │  security_engineer → Review security           │
    │  qa_engineer → Write tests                     │
    │  devops_engineer → Create CI/CD                │
    │                                                  │
    └─────────────────────────────────────────────────┘
         │                                            │
         └─→ Results back to Claude/Copilot ←───────┘
             Fully implemented authentication system
```

## File Structure

```
super-agents/
├── company/
│   ├── agent_registry.yaml              ← Agent configurations (9 agents)
│   ├── agent_support.py                 ← Core module (400+ lines)
│   ├── cli.py                           ← CLI interface (300+ lines)
│   ├── agents/                          ← Super-agent specs
│   │   ├── *_agent.yaml                 (22 agents)
│   │   └── ...
│   │
│   ├── .claude/commands/                ← Claude-specific commands
│   │   ├── super-agents-init.md
│   │   ├── list-agents.md
│   │   ├── agent-help.md
│   │   └── delegate-task.md
│   │
│   ├── .github/prompts/                 ← Copilot-specific commands
│   │   ├── super-agents-init.md
│   │   ├── list-agents.md
│   │   ├── agent-help.md
│   │   └── delegate-task.md
│   │
│   ├── .gemini/commands/                ← Gemini-specific commands (TOML)
│   │   ├── super-agents-init.toml
│   │   ├── list-agents.toml
│   │   ├── agent-help.toml
│   │   └── delegate-task.toml
│   │
│   ├── .agents/commands/                ← Amp-specific commands
│   ├── .cursor/commands/                ← Cursor-specific commands
│   ├── .windsurf/workflows/             ← Windsurf-specific commands
│   └── ... (other agent folders)
│
├── scripts/
│   ├── update-agent-context.sh          ← Bash context updater
│   └── update-agent-context.ps1         ← PowerShell context updater
│
├── QUICKSTART.md                        ← Fast onboarding (5 min)
├── MULTI_AGENT_SUPPORT.md               ← Full documentation
├── IMPLEMENTATION_SUMMARY.md            ← Implementation overview
└── SYSTEM_OVERVIEW.md                   ← This file
```

## Key Components

### 1. Agent Registry (`agent_registry.yaml`)
Centralized configuration for all supported AI agents:
- Agent ID and display name
- Storage directory (agent-specific)
- File format (Markdown vs TOML)
- CLI tool information
- Argument placeholders

### 2. Agent Support Module (`agent_support.py`)
Core Python module providing:
- Agent detection and registration
- Dynamic command generation (format-aware)
- Context file creation
- Super-agent spec loading
- Clean, reusable API

### 3. CLI Interface (`cli.py`)
Command-line tool with 8 commands:
- `detect` - Find available agents
- `init` - Initialize for agents
- `context` - Create context files
- `list-agents` - List super-agents
- `show-agent` - Show agent details
- `status` - System status
- `check` - Prerequisites check

### 4. Context Update Scripts
- **Bash** (`update-agent-context.sh`) - POSIX systems
- **PowerShell** (`update-agent-context.ps1`) - Windows systems

### 5. Generated Commands
Auto-generated agent-specific files:
- **Markdown format** for most agents (Claude, Copilot, Amp, etc.)
- **TOML format** for some agents (Gemini, Qwen)
- Placed in agent-specific directories

## Supported Agents

| Agent | Type | Format | Status |
|-------|------|--------|--------|
| Claude Code | CLI | Markdown | ✓ Ready |
| GitHub Copilot | IDE | Markdown | ✓ Ready |
| Amp | CLI | Markdown | ✓ Ready |
| Cursor | CLI | Markdown | ✓ Ready |
| Windsurf | IDE | Markdown | ✓ Ready |
| Amazon Q Developer | CLI | Markdown | ✓ Ready |
| Kilo Code | IDE | Markdown | ✓ Ready |
| Gemini CLI | CLI | TOML | ✓ Ready |
| Qwen Code | CLI | TOML | ✓ Ready |

## How It Works

### Phase 1: Registration
```
agent_registry.yaml defines:
- 9 supported AI agents
- Configuration for each
- Default commands to generate
```

### Phase 2: Detection
```
System checks which agents are available:
- CLI agents: checks if CLI tool installed
- IDE agents: assumes available
- Creates list of usable agents
```

### Phase 3: Initialization
```
For each selected agent:
1. Load agent configuration
2. Load super-agent specifications
3. Generate commands in agent-specific format
4. Place in agent-specific directories
```

### Phase 4: Context Management
```
Creates context files containing:
- List of super-agents
- Their capabilities and missions
- Delegation patterns
- Usage examples
```

### Phase 5: Agent Coordination
```
External agent uses generated commands:
/super-agents-init          → Learn about system
/list-agents                → See all agents
/agent-help <agent_id>      → Get agent details
/delegate-task <id>: <task> → Assign work
```

## Design Patterns

### 1. Agent-Agnostic Registry
- Single source of truth for agent metadata
- No hardcoded agent-specific logic
- Easy to add new agents

### 2. Format-Aware Generation
- Markdown for most agents
- TOML for some agents
- Automatically selects correct format

### 3. Modular Architecture
- Agent registry: Configuration
- Agent support: Core logic
- CLI: User interface
- Scripts: Automation

### 4. Configuration-Driven
- Extensible without code changes
- Easy agent onboarding
- Clear agent responsibilities

## Comparison with Spec Kit

Both systems follow the same design philosophy:

| Aspect | Spec Kit | Super-Agents |
|--------|----------|--------------|
| **Architecture** | Agent-agnostic registry | Agent-agnostic registry |
| **Supported Agents** | 13+ | 9+ |
| **Formats** | Markdown, TOML, etc. | Markdown, TOML |
| **Extension** | Configuration-based | Configuration-based |
| **Use Case** | Build from specs | Coordinate with agents |
| **CLI** | specify | Custom CLI |

Both demonstrate that:
- One system can support multiple agents
- Registry-based design is scalable
- Format agnosticism is powerful
- Configuration > hardcoding

## Quick Start

```bash
# 1. Initialize for Claude
cd company
python3 -c "from agent_support import AgentSupport; AgentSupport('.').initialize_for_agent('claude')"

# 2. Check generated files
ls .claude/commands/

# 3. View the initialization guide
cat .claude/commands/super-agents-init.md

# 4. Use in Claude Code
# Open Claude and run:
# /super-agents-init
# /list-agents
# /delegate-task backend_engineer: Design authentication API
```

## Documentation

- **QUICKSTART.md** - 5-minute quickstart
- **MULTI_AGENT_SUPPORT.md** - Complete reference
- **IMPLEMENTATION_SUMMARY.md** - What was built and why
- **SYSTEM_OVERVIEW.md** - This file (architecture)

## Next Steps

1. **Initialize**: `python3 cli.py init --agent claude`
2. **Verify**: `ls .claude/commands/` (check generated files)
3. **Learn**: Read `QUICKSTART.md` for examples
4. **Use**: Start delegating tasks in your AI agent
5. **Extend**: Add more agents with `python3 cli.py init --all`

## Benefits

✓ **Multi-Agent Support** - Works with 9+ AI agents
✓ **Automatic Formatting** - Commands auto-formatted per agent
✓ **Easy Setup** - One command to initialize
✓ **Extensible** - Add agents by updating registry
✓ **Well-Documented** - 1000+ lines of documentation
✓ **Tested** - Verified against multiple agent types
✓ **Maintainable** - Clean, modular architecture
✓ **Developer-Friendly** - Simple Python API

---

**Status**: ✓ Complete and ready to use
**Version**: 1.0
**Last Updated**: 2025
