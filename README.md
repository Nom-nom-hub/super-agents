# Super Agents

AICODE Labs - AI-native software development framework with autonomous agents

## Project Structure

This project follows a well-organized structure to separate concerns and improve maintainability:

```
super-agents/
├── super_agents/                   # Main Python package
│   ├── __init__.py
│   ├── README.md                   # Package documentation
│   ├── agent_registry.yaml         # Registry of available agents
│   ├── agent_support.py            # Agent support functionality
│   ├── runtime_config.yaml         # Runtime configuration
│   ├── .claude/                    # Claude-specific configurations
│   ├── agents/                     # Agent implementations and specs
│   │   ├── __init__.py
│   │   ├── agent_support.py
│   │   ├── ai_engineer_agent.yaml
│   │   ├── backend_engineer_agent.yaml
│   │   ├── builder_engineer_agent.yaml
│   │   ├── ceo_agent.yaml
│   │   ├── coo_agent.yaml
│   │   ├── cto_agent.yaml
│   │   ├── devops_engineer_agent.yaml
│   │   ├── finance_agent.yaml
│   │   ├── frontend_engineer_agent.yaml
│   │   ├── knowledge_architect_agent.yaml
│   │   ├── market_analyst_agent.yaml
│   │   ├── meta_architect_agent.yaml
│   │   ├── ops_automator_agent.yaml
│   │   ├── partnership_agent.yaml
│   │   ├── product_manager_agent.yaml
│   │   ├── prompt_engineer_agent.yaml
│   │   ├── qa_engineer_agent.yaml
│   │   ├── reflection_agent.py
│   │   ├── reliability_engineer_agent.yaml
│   │   ├── research_agent.yaml
│   │   ├── security_engineer_agent.yaml
│   │   ├── tech_writer_agent.yaml
│   │   ├── ux_designer_agent.yaml
│   │   └── types/                  # Specific agent type implementations
│   ├── cli/                        # Command-line interface
│   │   ├── __init__.py
│   │   ├── main.py                 # CLI entry point
│   │   ├── ui.py                   # CLI user interface
│   │   ├── ui_fixed.py             # Fixed version of CLI UI
│   │   └── ...                     # Other CLI components
│   ├── core/                       # Core logic and functionality
│   │   ├── __init__.py
│   │   ├── agent_orchestrator.py   # Agent orchestration
│   │   ├── agent_spec_validator.py # Agent specification validation
│   │   ├── autonomous_spec_manager.py # Autonomous spec management
│   │   ├── delegation_prompt_generator.py # Delegation prompt generation
│   │   ├── execution_tracker.py    # Execution tracking
│   │   ├── learning_integration.py # Learning integration
│   │   └── context_management_system.md # Context management documentation
│   ├── schemas/                    # Data schemas
│   │   └── agent_spec.json         # Agent specification schema
│   └── utils/                      # Utility functions
│       ├── __init__.py
│       ├── security_config.py      # Security configuration
│       └── structured_logging.py   # Structured logging
├── docs/                           # Documentation
│   ├── index.md
│   ├── getting_started.md
│   ├── architecture.md
│   ├── agents/
│   │   ├── index.md
│   │   ├── creating_agents.md
│   │   └── agent_lifecycle.md
│   ├── cli/
│   │   ├── index.md
│   │   └── commands.md
│   └── api/
│       ├── index.md
│       └── reference.md
├── tests/                          # Tests
├── examples/                       # Example implementations
├── scripts/                        # Utility scripts
├── logs/                           # Runtime logs
│   └── ...
├── .github/                        # GitHub configuration
├── pyproject.toml                  # Project configuration
├── README.md                       # Main project documentation
├── LICENSE                         # License file
├── Makefile                        # Make commands
├── SECURITY.md                     # Security policy
├── LINTING_FIXES.md                # Linting fixes documentation
└── requirements.txt                # Dependencies
```

## Installation

```bash
pip install super-agents
```

## Usage

To start the Super Agents CLI:

```bash
python -m super_agents.cli.main
# or
python3 super_agents/cli/main.py
```

To initialize super-agents:

```bash
python -m super_agents.cli.main init
```

To list available commands:

```bash
python -m super_agents.cli.main --help
```

## Development

To set up the development environment:

```bash
pip install -e ".[dev]"
```

To run tests:

```bash
pytest
```

To run linting:

```bash
make lint
```

To format code:

```bash
make format
```

To run all checks:

```bash
make check
```

## Contributing

We welcome contributions to the Super Agents project! Please follow these steps:

1. Fork the repository
1. Create a feature branch (`git checkout -b feature/amazing-feature`)
1. Make your changes
1. Add tests for your changes (if applicable)
1. Run `make check` to ensure all tests and linting pass
1. Commit your changes (`git commit -m 'Add amazing feature'`)
1. Push to the branch (`git push origin feature/amazing-feature`)
1. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
