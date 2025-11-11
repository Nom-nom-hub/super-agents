# Super Agents

AICODE Labs - AI-native software development company composed of autonomous agents

## Project Structure

This project follows a well-organized structure to separate concerns and improve maintainability:

```
super-agents/
├── .qwen/                          # Runtime configuration files
│   ├── agents/                     # Agent-specific configurations
│   ├── contexts/                   # Context files and runtime state
│   ├── logs/                       # Runtime logs
│   ├── cache/                      # Cache files
│   └── config.yaml                 # Main runtime configuration
├── super_agents/                   # Main Python package
│   ├── __init__.py
│   ├── core/                       # Core logic and functionality
│   │   ├── __init__.py
│   │   ├── agent.py                # Agent base class
│   │   ├── orchestrator.py         # Agent orchestration
│   │   ├── registry.py             # Agent registry
│   │   └── context_manager.py      # Context management
│   ├── agents/                     # Agent implementations
│   │   ├── __init__.py
│   │   ├── base.py                 # Base agent functionality
│   │   ├── registry.py             # Agent registry
│   │   └── types/                  # Specific agent types
│   │       ├── __init__.py
│   │       ├── engineer.py
│   │       ├── researcher.py
│   │       └── coordinator.py
│   ├── cli/                        # Command-line interface
│   │   ├── __init__.py
│   │   ├── main.py                 # CLI entry point
│   │   └── commands/               # CLI commands
│   │       ├── __init__.py
│   │       ├── init.py
│   │       ├── run.py
│   │       └── status.py
│   ├── utils/                      # Utility functions
│   │   ├── __init__.py
│   │   ├── logging.py
│   │   └── validation.py
│   └── schemas/                    # Data schemas
│       ├── __init__.py
│       ├── agent_spec.json
│       └── config_schema.json
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
│   ├── __init__.py
│   ├── unit/                       # Unit tests
│   │   ├── __init__.py
│   │   ├── test_agent.py
│   │   └── test_orchestrator.py
│   ├── integration/                # Integration tests
│   │   ├── __init__.py
│   │   └── test_end_to_end.py
│   └── fixtures/                   # Test fixtures
│       └── sample_agent_spec.json
├── examples/                       # Example implementations
│   ├── simple_agent.py
│   ├── multi_agent_system.py
│   └── custom_agent.py
├── scripts/                        # Utility scripts
│   ├── setup_dev_env.sh
│   ├── run_tests.sh
│   └── build_docs.sh
├── .github/                        # GitHub configuration
│   └── workflows/
│       ├── tests.yml
│       └── publish.yml
├── pyproject.toml                  # Project configuration
├── README.md                       # Main project documentation
├── CHANGELOG.md                    # Change log
├── LICENSE                         # License file
├── Makefile                        # Make commands
└── requirements.txt                # Dependencies
```

## Installation

```bash
pip install super-agents
```

## Usage

To start the Super Agents system:

```bash
aicode
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

## Contributing

Please see our [Contributing Guide](CONTRIBUTING.md) for more information.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.