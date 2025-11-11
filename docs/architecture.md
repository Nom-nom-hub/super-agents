# Super Agents Architecture

This document describes the architecture of the Super Agents system, which follows a hybrid approach with a clear separation between the Python codebase and runtime configuration.

## Hybrid Architecture Overview

The Super Agents system is designed with a clear separation of concerns between:

1. **Python Codebase** (`super_agents/`): Contains all the core logic, algorithms, and functionality
2. **Runtime Configuration** (`.qwen/`): Contains runtime state, configurations, and context files

## Components

### Python Codebase (`super_agents/`)

The Python codebase is organized into several key modules:

- **Core (`super_agents/core/`)**: Contains fundamental classes and functions that power the agent system
  - Agent base classes and interfaces
  - Orchestration logic
  - Context management
  - Registry systems

- **Agents (`super_agents/agents/`)**: Contains agent implementations and types
  - Base agent functionality
  - Specific agent types (engineer, researcher, coordinator)
  - Agent communication protocols

- **CLI (`super_agents/cli/`)**: Command-line interface
  - Entry points for user interaction
  - Command implementations
  - UI components

- **Utils (`super_agents/utils/`)**: Utility functions and helpers
  - Logging utilities
  - Validation functions
  - Common utilities

- **Schemas (`super_agents/schemas/`)**: Data schemas and validation
  - JSON schemas for configuration
  - Data validation rules

### Runtime Configuration (`.qwen/`)

The runtime configuration directory contains files and state that change during operation:

- **Agents (`.qwen/agents/`)**: Agent-specific configurations that can be modified at runtime
- **Contexts (`.qwen/contexts/`)**: Runtime context and state information
- **Logs (`.qwen/logs/`)**: Runtime logs and debugging information
- **Cache (`.qwen/cache/`)**: Cached data and temporary files
- **Config (`.qwen/config.yaml`)**: Main runtime configuration

## Benefits of This Architecture

1. **Clear Separation**: Code and configuration are clearly separated, making maintenance easier
2. **Scalability**: Runtime state is isolated from core logic, allowing for better scaling
3. **Maintainability**: Changes to configuration don't require code changes
4. **Security**: Sensitive runtime information is isolated from the codebase
5. **Flexibility**: Different configurations can be used with the same codebase

## Development Workflow

1. Modify Python code in the `super_agents/` directory
2. Update runtime configurations in the `.qwen/` directory as needed
3. Test changes using the provided test suite
4. Document changes in the `docs/` directory