# Multi-Agent Support for Super-Agents

This document explains how to integrate AICODE Labs super-agents with external AI agents (Claude, Copilot, Amp, Gemini, etc.).

Inspired by GitHub Spec Kit's agent-agnostic design pattern, Super-Agents can now work seamlessly with multiple AI platforms.

## Overview

Super-Agents provides:

- **Agent Registry**: Configuration for all supported AI agents
- **Agent Support Module**: Python API for agent integration
- **CLI Tool**: Command-line interface for initialization
- **Context Scripts**: Bash and PowerShell scripts for agent context management
- **Command Templates**: Pre-built commands for each agent format (Markdown, TOML, etc.)

## Supported AI Agents

| Agent | CLI Tool | Format | Status |
|-------|----------|--------|--------|
| Claude Code | `claude` | Markdown | ✓ Supported |
| GitHub Copilot | IDE | Markdown | ✓ Supported |
| Amp | `amp` | Markdown | ✓ Supported |
| Gemini CLI | `gemini` | TOML | ✓ Supported |
| Cursor | `cursor-agent` | Markdown | ✓ Supported |
| Windsurf | IDE | Markdown | ✓ Supported |
| Amazon Q Developer | `q` | Markdown | ✓ Supported |
| Qwen Code | `qwen` | TOML | ✓ Supported |
| Kilo Code | IDE | Markdown | ✓ Supported |

## Quick Start

### 1. Detect Available Agents

```bash
cd company
python cli.py detect
```

Shows which AI agents are installed on your system.

### 2. Initialize for an Agent

```bash
# Initialize for Claude
python cli.py init --agent claude

# Initialize for GitHub Copilot
python cli.py init --agent copilot

# Initialize for Amp
python cli.py init --agent amp

# Initialize for all available agents
python cli.py init --all
```

This creates agent-specific command files in the agent's directory:
- Claude: `.claude/commands/`
- Copilot: `.github/prompts/`
- Amp: `.agents/commands/`
- Etc.

### 3. Use Super-Agents in Your AI Agent

Once initialized, your agent can:

1. **List available super-agents**:
   ```
   /list-agents
   ```

2. **Get help about a specific agent**:
   ```
   /agent-help backend_engineer
   ```

3. **Delegate tasks**:
   ```
   /delegate-task backend_engineer: Design a REST API for user management
   /delegate-task ux_designer: Create wireframes for mobile app
   /delegate-task qa_engineer: Write integration tests for payment flow
   ```

## Agent Registry

The agent registry is defined in `company/agent_registry.yaml`:

```yaml
agents:
  claude:
    name: "Claude Code"
    folder: ".claude/commands/"
    format: "markdown"
    cli_tool: "claude"
    install_url: "https://docs.anthropic.com/claude/reference/claude-code"
    requires_cli: true
    placeholder: "$ARGUMENTS"
    file_extension: "md"
```

**Fields**:
- `name`: Display name for the agent
- `folder`: Where to store agent-specific files
- `format`: File format (markdown, toml)
- `cli_tool`: CLI tool name (if applicable)
- `install_url`: Installation documentation URL
- `requires_cli`: Whether a CLI tool is required
- `placeholder`: Argument placeholder format
- `file_extension`: File extension for generated commands

## Python API

### Basic Usage

```python
from agent_support import AgentSupport

# Initialize
support = AgentSupport("company")

# Detect available agents
available = support.get_available_agents()
print(f"Available agents: {available}")

# Initialize for an agent
support.initialize_for_agent("claude")

# Load super-agent specifications
specs = support.load_agent_specs()
for agent_id, spec in specs.items():
    print(f"{agent_id}: {spec['title']}")
```

### Detecting Agents

```python
# Check which agents are available
available = support.detect_available_agents()
for agent_id, is_available in available.items():
    status = "✓" if is_available else "✗"
    print(f"{status} {agent_id}")
```

### Generating Commands

```python
# Generate commands for a specific agent
support.generate_agent_commands("claude")

# Create unified context file
support.create_agent_context_file("copilot")
```

### Loading Super-Agent Specs

```python
# Load all super-agent specifications
specs = support.load_agent_specs()

# Access specific agent
backend_spec = specs.get("backend_engineer")
print(f"Capabilities: {backend_spec['capabilities']}")
print(f"Delegates to: {backend_spec['delegates_to']}")
```

## CLI Commands

### detect
Detect available AI agents on the system.

```bash
python cli.py detect
```

Output:
```
📊 AI Agent Detection Report

┌─────────┬──────────────────┬────────────┬──────────────┐
│ Agent   │ Name             │ CLI Tool   │ Status       │
├─────────┼──────────────────┼────────────┼──────────────┤
│ claude  │ Claude Code      │ claude     │ ✓ Available  │
│ copilot │ GitHub Copilot   │ IDE-based  │ ✓ Available  │
│ amp     │ Amp              │ amp        │ ✗ Not Found  │
└─────────┴──────────────────┴────────────┴──────────────┘
```

### init
Initialize super-agents for AI agents.

```bash
# Specific agent
python cli.py init --agent claude

# All available
python cli.py init --all

# Interactive mode
python cli.py init
```

### list-agents
List all super-agents in the system.

```bash
python cli.py list-agents
```

### show-agent
Show details about a specific super-agent.

```bash
python cli.py show-agent --agent backend_engineer
```

Output:
```
Backend Engineer
============================================================

ID: backend_engineer
Division: Engineering

Mission:
  Design and implement backend services, APIs, and data layers
  using Python, FastAPI, and scalable cloud infrastructure.

Capabilities:
  • API Design and Implementation
  • Database Architecture
  • Microservices Design
  • Performance Optimization
  • Scalability Planning

...
```

### status
Show system status.

```bash
python cli.py status
```

### check
Check system prerequisites.

```bash
python cli.py check
```

## Context Update Scripts

### Bash/POSIX

Update agent context for all agents or specific ones:

```bash
# Update all agents
bash scripts/update-agent-context.sh

# Update specific agent
bash scripts/update-agent-context.sh claude
bash scripts/update-agent-context.sh copilot
```

### PowerShell

```powershell
# Update all agents
.\scripts\update-agent-context.ps1

# Update specific agent
.\scripts\update-agent-context.ps1 -AgentType claude
.\scripts\update-agent-context.ps1 -AgentType copilot
```

## How It Works

### 1. Agent Registration

Each AI agent (Claude, Copilot, Amp, etc.) is registered in `agent_registry.yaml` with:
- Where to store agent-specific files
- What format to use (Markdown vs TOML)
- How to invoke commands (placeholder format)

### 2. Command Generation

When you initialize for an agent, Super-Agents generates:

**For Markdown-based agents** (Claude, Copilot, Amp, Cursor, Windsurf):
```markdown
# super-agents-init.md
# Super-Agents Initialization for Claude Code

You now have access to AICODE Labs super-agents...
```

**For TOML-based agents** (Gemini, Qwen):
```toml
# super-agents-init.toml
description = "Initialize connection to super-agents"
prompt = """..."""
```

### 3. Context Management

Context files in each agent's directory contain:
- List of available super-agents
- Their capabilities and missions
- Delegation patterns
- Usage examples

### 4. Agent Communication

Your external AI agent (Claude, Copilot, etc.) can coordinate with super-agents using:

```
@agent_id: Task description
```

Example workflow:
```
User: "Build a user authentication system"

Claude: I'll coordinate with the team.

Claude → @backend_engineer: Design authentication API
Claude → @frontend_engineer: Build login UI
Claude → @security_engineer: Review security implementation
Claude → @qa_engineer: Write authentication tests

Super-Agents execute in parallel, report back to Claude
Claude: Here's the complete authentication system...
```

## Adding New Agents

To add support for a new AI agent:

1. **Update agent_registry.yaml**:
```yaml
new_agent:
  name: "New Agent Name"
  folder: ".newagent/commands/"
  format: "markdown"  # or "toml"
  cli_tool: "new-agent-cli"
  install_url: "https://..."
  requires_cli: true
  placeholder: "$ARGUMENTS"
  file_extension: "md"
```

2. **Update agent_support.py** (if custom format needed):
   - Add format handler in `_generate_command_content()`

3. **Update scripts** (if custom directory structure):
   - Add agent folder mapping in `update-agent-context.sh`
   - Add agent folder mapping in `update-agent-context.ps1`

4. **Test**:
```bash
python cli.py init --agent new_agent
python cli.py show-agent --agent new_agent
```

## Files Created

```
company/
├── agent_registry.yaml           # Agent configurations
├── agent_support.py              # Core module
├── cli.py                        # CLI interface
└── agents/                       # Super-agent specs
    ├── backend_engineer_agent.yaml
    ├── frontend_engineer_agent.yaml
    ├── ux_designer_agent.yaml
    └── ... (other agents)

.claude/                           # Claude-specific files
├── commands/
│   ├── super-agents-init.md
│   ├── list-agents.md
│   ├── agent-help.md
│   └── delegate-task.md

.github/                           # Copilot-specific files
├── prompts/
│   ├── super-agents-init.md
│   ├── list-agents.md
│   └── ...

.agents/                           # Amp-specific files
├── commands/
│   └── ...

scripts/
├── update-agent-context.sh       # Bash context update
└── update-agent-context.ps1      # PowerShell context update
```

## Examples

### Example 1: Initialize for Claude Code

```bash
cd company
python cli.py init --agent claude
```

Result:
```
🤖 Initializing Super-Agents for Claude Code...
✓ Generated super-agents-init.md for Claude Code
✓ Generated list-agents.md for Claude Code
✓ Generated agent-help.md for Claude Code
✓ Generated delegate-task.md for Claude Code
✓ Super-agents initialized in .claude/commands/

Next steps:
  1. Open .claude/commands/super-agents-init.md
  2. Use commands in your Claude Code environment
  3. Start delegating tasks to super-agents!
```

Claude now has access to commands like:
```
/super-agents-init
/list-agents
/agent-help backend_engineer
/delegate-task backend_engineer: Create user authentication API
```

### Example 2: Initialize for All Available Agents

```bash
python cli.py init --all
```

Result:
```
🤖 Initializing Super-Agents for 3 available agents...

✓ Generated super-agents-init.md for Claude Code
✓ Generated list-agents.md for Claude Code
✓ Generated agent-help.md for Claude Code
✓ Generated delegate-task.md for Claude Code

✓ Generated super-agents-init.md for GitHub Copilot
✓ Generated list-agents.md for GitHub Copilot
✓ Generated agent-help.md for GitHub Copilot
✓ Generated delegate-task.md for GitHub Copilot

✓ Generated super-agents-init.md for Amp
✓ Generated list-agents.md for Amp
✓ Generated agent-help.md for Amp
✓ Generated delegate-task.md for Amp

✓ Successfully initialized 3 agents
```

Now Claude, Copilot, and Amp can all coordinate with super-agents!

### Example 3: Show Agent Information

```bash
python cli.py show-agent --agent backend_engineer
```

Output:
```
Backend Engineer
============================================================

ID: backend_engineer
Division: Engineering

Mission:
  Design and implement backend services, APIs, and data layers
  using Python, FastAPI, and scalable cloud infrastructure.

Capabilities:
  • API Design and Implementation
  • Database Architecture
  • Microservices Design
  • Performance Optimization
  • Scalability Planning

Tools:
  • Python 3.11+
  • FastAPI
  • PostgreSQL
  • Docker
  • Kubernetes

Accepts:
  • Product specifications
  • API requirements
  • Database schemas
  • Integration specifications

Produces:
  • RESTful API implementations
  • Database migrations
  • API documentation
  • Performance benchmarks

Delegates To:
  • DevOps Engineer
  • Security Engineer
  • QA Engineer
============================================================
```

## Best Practices

1. **Initialize Early**: Run `python cli.py init --all` when setting up a project
2. **Keep Registry Updated**: Update `agent_registry.yaml` when using new agents
3. **Update Context**: Run context update scripts when agent specs change
4. **Document Tasks**: Be specific when delegating to super-agents
5. **Sequential Workflows**: Chain super-agents for complex features

## Troubleshooting

### "Agent registry not found"
Make sure you're in the right directory and `agent_registry.yaml` exists.

```bash
ls company/agent_registry.yaml
```

### "Unknown agent"
Check registered agents:
```bash
python cli.py detect
```

### "CLI tool not found"
Install the agent's CLI tool:
```bash
# Claude
npm install -g @anthropic-ai/claude-cli

# Amp
npm install -g @sourcegraph/amp

# Gemini
pip install google-gemini-cli
```

### Agent commands not working
Make sure the commands were generated:
```bash
ls .claude/commands/
ls .github/prompts/
ls .agents/commands/
```

## Future Enhancements

- VS Code extension for super-agents
- Integration with GitHub Issues
- Web UI for agent coordination
- Real-time agent monitoring
- Agent performance metrics
- Custom agent templates
- Multi-language support

## See Also

- `company/agent_orchestrator.py` - Super-agent orchestration
- `company/agent_registry.yaml` - Agent registry
- `company/agents/` - Super-agent specifications
- GitHub Spec Kit: https://github.com/github/spec-kit
