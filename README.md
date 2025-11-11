# AICODE Labs - Super-Agents

A full AI-native software development company composed entirely of autonomous agents. This system implements an organization of specialized AI agents that can collaborate to design, develop, test, deploy, and maintain software products from conception to production.

## Installation

### Using uv (Recommended)

```bash
# Install from GitHub with uv
uv pip install git+https://github.com/Nom-nom-hub/super-agents.git

# Or for development
uv pip install --editable git+https://github.com/Nom-nom-hub/super-agents.git
```

### Using pip

```bash
# Install from GitHub with pip
pip install git+https://github.com/Nom-nom-hub/super-agents.git
```

## Quick Start

After installation, initialize the system for your preferred AI agent:

```bash
# Initialize for Claude
aicode init --agent claude

# Initialize for Copilot (IDE-based)
aicode init --agent copilot

# Initialize for all available agents
aicode init --all
```

## Available Agents

The system supports integration with various AI agents:

- **Claude** - Anthropic's Claude Code
- **Copilot** - GitHub Copilot (IDE-based)
- **Amp** - Sourcegraph's Amp
- **Gemini** - Google's Gemini CLI
- **Cursor** - Cursor IDE
- **Windsurf** - Windsurf IDE
- **Amazon Q** - AWS Q Developer CLI
- **Qwen** - Alibaba Qwen Code
- **Kilo Code** - Kilo Code IDE

## Super-Agent Organization

AICODE Labs features 22 specialized agents across 8 divisions:

### Executive Division

- **CEO** - Strategic direction and resource allocation
- **CTO** - Technical architecture and standards  
- **COO** - Operations and workflow management

### Product Division

- **Product Manager** - Requirements and specifications
- **UX Designer** - User experience and interface design
- **Market Analyst** - Market research and insights

### Engineering Division

- **Backend Engineer** - API services and business logic
- **Frontend Engineer** - UI components and client-side logic
- **AI Engineer** - AI models and reasoning chains
- **DevOps Engineer** - Infrastructure and deployment
- **Builder Engineer** - Code generation from specs

### Quality Division

- **QA Engineer** - Testing and quality assurance
- **Reliability Engineer** - System health and monitoring

### Security Division

- **Security Engineer** - Authentication and security policies

### Knowledge Division

- **Tech Writer** - Documentation and guides
- **Knowledge Architect** - Knowledge management

### Governance Division

- **Meta Architect** - System evolution and compliance

### Expansion Division

- **Finance Agent** - Budget and resource allocation
- **Partnership Agent** - External integrations
- **Prompt Engineer** - Prompt optimization
- **Research Agent** - Technology research
- **Ops Automator** - Process automation

## Usage

### List available super-agents

```bash
aicode list-agents
```

**Note**: If you encounter import errors with the `aicode` command, you can run the CLI directly using Python module execution:

```bash
python -m company.cli list-agents
```

### Get details about a specific agent

```bash
aicode show-agent --agent backend_engineer
```

Or using the module approach:

```bash
python -m company.cli show-agent --agent backend_engineer
```

### Generate context for an agent

```bash
aicode context --agent claude
```

### Check system status

```bash
aicode status
```

## Agent Integration

Once initialized, external AI agents can delegate tasks to the super-agent organization using the following patterns:

```
@backend_engineer: Design a REST API for user management
@ux_designer: Create wireframes for the dashboard
@security_engineer: Implement OAuth2 authentication
@qa_engineer: Write integration tests for the payment flow
```

## How It Works

The system provides external AI agents with comprehensive context files that enable them to coordinate with specialized autonomous agents within the AICODE Labs organization. Each external agent gets:

- Agent specifications and capabilities
- Task delegation patterns
- Context information
- Collaboration guidelines
- Response templates

## Contributing

Contributions are welcome! Please see the contributing guidelines in the repository.

## License

MIT License - see the LICENSE file for details.
