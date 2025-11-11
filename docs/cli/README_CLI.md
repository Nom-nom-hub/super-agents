# AICODE Labs Super-Agents CLI

## Overview

The AICODE Labs Super-Agents CLI provides a comprehensive system for initializing and managing AI agents to work with the AICODE Labs organization of autonomous agents. The system allows external AI agents (like Claude, Copilot, Gemini, etc.) to interface with and delegate tasks to specialized super-agents within the AICODE Labs ecosystem.

## CLI Commands

### `aicode init`
Initialize an external AI agent with comprehensive files and context to work with super-agents.

**Options:**
- `-a, --agent TEXT`: Specific agent to initialize (claude, copilot, amp, gemini, cursor, etc.)
- `--all`: Initialize for all available agents
- `-s, --script TEXT`: Run a script after initialization
- `-p, --project TEXT`: Project context to use for initialization

**Usage:**
```bash
# Initialize a specific agent (e.g., Claude)
aicode init --agent claude

# Initialize with a specific project context
aicode init --agent copilot --project my-project

# Initialize all available agents
aicode init --all
```

### `aicode list-agents`
List all super-agents in the system with their capabilities and missions.

### `aicode show-agent --agent <agent-id>`
Show detailed information about a specific super-agent.

### `aicode context --agent <agent-id>`
Create a unified context file containing all super-agent specifications.

### `aicode detect`
Detect available AI agents on the system.

### `aicode status`
Show system status and statistics.

### `aicode check`
Check system prerequisites and configuration.

## Agent Initialization Files

When you run `aicode init --agent <agent-name>`, the system creates comprehensive files for the selected agent:

### Directory Structure
```
<agent-folder>/ (e.g., .claude/commands/, .github/prompts/, etc.)
├── agent_profile.yaml              # Agent-specific profile
├── context/                        # Context and project information
│   ├── project_context.json        # Project-specific context
│   ├── shared_memories/            # Shared organizational knowledge
│   └── agent_memories/             # Agent-specific memory
├── specs/                          # Specifications and requirements
│   ├── agent_specs.yaml            # Agent specifications
│   └── task_requirements.md        # Task-specific requirements
├── resources/                      # Tools and dependencies
│   ├── tools.json                  # Available tools
│   └── dependencies.txt            # Dependencies list
├── workflows/                      # Procedures and guidelines
│   ├── standard_operating_procedures.md
│   └── collaboration_guidelines.md
├── templates/                      # Response templates
│   └── response_template.md
├── division_specific/              # Division-specific context (if applicable)
│   └── <division>_context.md
├── super-agents-init.md            # Main initialization guide
├── list-agents.md                  # List of available super-agents
├── agent-help.md                   # Help for specific agents
├── delegate-task.md                # Task delegation instructions
└── super-agents-context.yaml       # Unified context with all super-agent specs
```

### Key Files Description

1. **agent_profile.yaml**: Configuration specific to the initialized agent
2. **project_context.json**: Project-specific information and constraints
3. **task_requirements.md**: Template for understanding task requirements
4. **response_template.md**: Structured template for agent responses
5. **super-agents-context.yaml**: Complete specification of all super-agents
6. **Standard command files**: Initialization, listing, help, and delegation guides

## Super-Agent System

The AICODE Labs system includes 22 specialized agents across 8 divisions:

### Executive Division
- **CEO**: Strategic direction and resource allocation
- **CTO**: Technical architecture and standards  
- **COO**: Operations and workflow management

### Product Division
- **Product Manager**: Requirements and specifications
- **UX Designer**: User experience and interface design
- **Market Analyst**: Market research and insights

### Engineering Division
- **Backend Engineer**: API services and business logic
- **Frontend Engineer**: UI components and client-side logic
- **AI Engineer**: AI models and reasoning chains
- **DevOps Engineer**: Infrastructure and deployment
- **Builder Engineer**: Code generation from specs

### Quality Division
- **QA Engineer**: Testing and quality assurance
- **Reliability Engineer**: System health and monitoring

### Security Division
- **Security Engineer**: Authentication and security policies

### Knowledge Division
- **Tech Writer**: Documentation and guides
- **Knowledge Architect**: Knowledge management

### Governance Division
- **Meta Architect**: System evolution and compliance

### Expansion Division
- **Finance Agent**: Budget and resource allocation
- **Partnership Agent**: External integrations
- **Prompt Engineer**: Prompt optimization
- **Research Agent**: Technology research
- **Ops Automator**: Process automation

## How to Use Super-Agents

After initialization, the external agent can use the following commands within their environment:

1. **View all agents**: Use the information in `list-agents.md`
2. **Get agent details**: Use `agent-help.md` guidelines
3. **Delegate tasks**: Use the patterns in `delegate-task.md`
4. **Access full specs**: All agent specifications in `super-agents-context.yaml`

## Agent Command Patterns

When delegating tasks, use these patterns:

```
/delegate-task <agent_id>: <task_description>
```

Examples:
- `/delegate-task backend_engineer: Design a REST API for user management`
- `/delegate-task ux_designer: Create wireframes for the dashboard`
- `/delegate-task security_engineer: Implement OAuth2 authentication`
- `/delegate-task qa_engineer: Write integration tests for the payment flow`

## Project Integration

The system supports project-specific contexts that can be provided during initialization using the `--project` option. This allows agents to work within specific project constraints and requirements.

## Error Handling

If agent initialization fails, the system will provide specific error messages indicating:
- Unknown agent type
- Missing registry entries
- File system permissions issues
- Invalid configuration

## Extensibility

The system is designed to be extensible:
- New external agents can be added to the registry
- New super-agents can be defined in YAML files
- Additional commands can be added to the default command set
- Custom initialization workflows can be implemented