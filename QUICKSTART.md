# Super-Agents Multi-Agent Support - Quick Start

## What Is This?

Super-Agents now integrates with multiple external AI agents (Claude, Copilot, Amp, Gemini, etc.) just like GitHub Spec Kit does. Your super-agents can be coordinated by any compatible AI agent.

## One-Minute Setup

### 1. Check Available Agents

```bash
cd company
python3 -c "
from agent_support import AgentSupport
support = AgentSupport('.')
print('Available agents:', support.list_registered_agents())
"
```

### 2. Generate Commands for an Agent

```bash
# For Claude Code
python3 -c "from agent_support import AgentSupport; AgentSupport('.').initialize_for_agent('claude')"

# For GitHub Copilot
python3 -c "from agent_support import AgentSupport; AgentSupport('.').initialize_for_agent('copilot')"

# For Amp
python3 -c "from agent_support import AgentSupport; AgentSupport('.').initialize_for_agent('amp')"
```

### 3. Use in Your Agent

Once initialized, your agent has access to:

```
/super-agents-init         # Learn about super-agents
/list-agents               # See all available agents
/agent-help <agent_id>     # Get info about a specific agent
/delegate-task <id>: <task> # Assign work
```

## Example

### For Claude Code

```bash
# 1. Initialize
cd company
python3 -c "from agent_support import AgentSupport; AgentSupport('.').initialize_for_agent('claude')"

# 2. Check generated files
ls .claude/commands/
# Output:
# agent-help.md
# delegate-task.md
# list-agents.md
# super-agents-init.md

# 3. View the initialization guide
cat .claude/commands/super-agents-init.md
```

In Claude Code, you now have:
```
/super-agents-init              # Initialize connection
/list-agents                    # View all agents
/agent-help backend_engineer    # Learn about an agent
/delegate-task backend_engineer: Design a REST API
```

### For GitHub Copilot

```bash
python3 -c "from agent_support import AgentSupport; AgentSupport('.').initialize_for_agent('copilot')"

ls .github/prompts/
# Output:
# agent-help.md
# delegate-task.md
# list-agents.md
# super-agents-init.md
```

### For Gemini CLI

```bash
python3 -c "from agent_support import AgentSupport; AgentSupport('.').initialize_for_agent('gemini')"

ls .gemini/commands/
# Output:
# agent-help.toml      (TOML format)
# delegate-task.toml
# list-agents.toml
# super-agents-init.toml
```

## What's New

### New Files

```
company/
├── agent_registry.yaml           # Agent configurations (9 agents)
├── agent_support.py              # Core module (300+ lines)
├── cli.py                        # CLI tool (8 commands)
├── .claude/commands/             # Claude-specific files
├── .github/prompts/              # Copilot-specific files
├── .gemini/commands/             # Gemini-specific files
├── .agents/commands/             # Amp-specific files
└── ... (other agent folders)

scripts/
├── update-agent-context.sh       # Bash context updater
└── update-agent-context.ps1      # PowerShell context updater
```

### New Features

1. **Agent Registry** - Configuration for 9 AI agents (Claude, Copilot, Amp, Gemini, Cursor, Windsurf, Amazon Q, Qwen, Kilo)
2. **Auto-Generated Commands** - Custom command files for each agent's format (Markdown vs TOML)
3. **CLI Tool** - Initialize and manage agents
4. **Context Scripts** - Update agent context with latest specs
5. **Python API** - Programmatic agent support

## Supported Agents

| Agent | CLI | Format | Status |
|-------|-----|--------|--------|
| Claude Code | `claude` | Markdown | ✓ Ready |
| GitHub Copilot | IDE | Markdown | ✓ Ready |
| Amp | `amp` | Markdown | ✓ Ready |
| Gemini CLI | `gemini` | TOML | ✓ Ready |
| Cursor | `cursor-agent` | Markdown | ✓ Ready |
| Windsurf | IDE | Markdown | ✓ Ready |
| Amazon Q Developer | `q` | Markdown | ✓ Ready |
| Qwen Code | `qwen` | TOML | ✓ Ready |
| Kilo Code | IDE | Markdown | ✓ Ready |

## How It Works

### 1. Agent Registry (`agent_registry.yaml`)

Defines how each agent integrates:
- Where to store commands (agent-specific directories)
- Command format (Markdown, TOML, etc.)
- CLI tool names
- Placeholder formats

### 2. Agent Support Module (`agent_support.py`)

Provides:
- Agent detection
- Command generation (auto-formatted for each agent)
- Context file creation
- Super-agent specification loading

### 3. Generated Commands

When you initialize for an agent, commands are auto-generated:

**For Markdown agents** (Claude, Copilot, Amp):
```markdown
# super-agents-init.md
## How to Use Super-Agents
### Delegate Tasks
/delegate-task backend_engineer: Design a REST API
```

**For TOML agents** (Gemini, Qwen):
```toml
[super-agents-init]
description = "Initialize super-agents"
prompt = """..."""
```

## API Examples

### Detect Available Agents

```python
from agent_support import AgentSupport

support = AgentSupport("company")
available = support.detect_available_agents()
# Returns: {'claude': True, 'copilot': True, 'amp': False, ...}
```

### Initialize for an Agent

```python
support.initialize_for_agent("claude")
# Creates: .claude/commands/{super-agents-init,list-agents,agent-help,delegate-task}.md
```

### Load Super-Agent Specs

```python
specs = support.load_agent_specs()
for agent_id, spec in specs.items():
    print(f"{agent_id}: {spec['title']}")
    print(f"  Mission: {spec['mission']}")
    print(f"  Capabilities: {spec['capabilities']}")
```

## Next Steps

1. **Initialize for your agent**: `python3 -c "from agent_support import AgentSupport; AgentSupport('.').initialize_for_agent('claude')"`
2. **Check generated files**: `ls .claude/commands/` (or `.github/prompts/`, etc.)
3. **View instructions**: `cat .claude/commands/super-agents-init.md`
4. **Use in your agent**: `/super-agents-init`, `/list-agents`, `/delegate-task`

## Full Documentation

See `MULTI_AGENT_SUPPORT.md` for:
- Detailed API documentation
- CLI command reference
- Context update scripts
- Adding new agents
- Troubleshooting

## Key Differences from Spec Kit

| Aspect | Spec Kit | Super-Agents |
|--------|----------|--------------|
| Purpose | External agents use specifications | External agents coordinate with internal agents |
| Direction | Agent generates code from spec | Agent delegates to specialized agents |
| Use Case | "Build what this spec describes" | "Coordinate with these specialized agents" |
| Output | Implementation code | Coordinated multi-agent work |

Both follow the same agent-agnostic design pattern!
