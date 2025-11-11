# AICODE Labs CLI - Agent Initialization System

## Command Overview

The `aicode init` command allows users to initialize agent-specific environments with all necessary files and context for effective operation.

## Command Syntax

```
aicode init <agent-type> [options]
```

### Agent Types
- `ceo` - Chief Executive Officer Agent
- `cto` - Chief Technology Officer Agent  
- `coo` - Chief Operations Officer Agent
- `product-manager` - Product Manager Agent
- `ux-designer` - UX/UI Designer Agent
- `market-analyst` - Market Analyst Agent
- `backend-engineer` - Backend Engineer Agent
- `frontend-engineer` - Frontend Engineer Agent
- `ai-engineer` - AI Engineer Agent
- `devops-engineer` - DevOps Engineer Agent
- `builder-engineer` - Spec Builder Agent
- `qa-engineer` - Quality Assurance Agent
- `reliability-engineer` - Reliability Engineer Agent
- `security-engineer` - Security Agent
- `tech-writer` - Technical Writer Agent
- `knowledge-architect` - Knowledge Architect Agent
- `meta-architect` - Meta Architect Agent
- `finance-agent` - Finance Agent
- `partnership-agent` - Partnership Agent
- `prompt-engineer` - Prompt Engineer Agent
- `research-agent` - Research Agent
- `ops-automator` - Operations Automator Agent

## Options

### Common Options
- `--project <project-name>` - Specify the project context to use
- `--task <task-description>` - Provide specific task context
- `--output <directory>` - Specify output directory (default: ./agent-init)
- `--verbose` - Show detailed initialization process
- `--dry-run` - Show what would be created without creating files
- `--config <config-file>` - Use custom configuration file

### Project Context Options
- `--project-file <file>` - Load project context from file
- `--create-project <name>` - Create new project context
- `--template <template-name>` - Use specific project template

### Advanced Options
- `--include-dependencies` - Include dependency files
- `--exclude-common` - Exclude common files (use with caution)
- `--custom-spec <file>` - Use custom agent specification file

## Example Usage

### Basic Initialization
```
# Initialize a backend engineer with default settings
aicode init backend-engineer

# Initialize a product manager for a specific project
aicode init product-manager --project ecommerce-platform

# Initialize with specific task context
aicode init frontend-engineer --task "implement-user-dashboard" --project dashboard-redesign
```

### Advanced Initialization
```
# Initialize with custom configuration
aicode init ai-engineer --config my-ai-config.yaml --project ml-platform

# Dry run to see what would be created
aicode init security-engineer --project banking-app --dry-run --verbose

# Initialize with specific output directory
aicode init devops-engineer --output /tmp/devops-agent --project ci-cd-upgrade
```

## Generated File Structure

The command generates agent-specific files as described in the agent_initialization_files.md document, including:

### Common Structure
```
<output-directory>/
├── agent_profile.yaml
├── context/
│   ├── project_context.json
│   ├── shared_memories/
│   └── agent_memories/
├── specs/
│   ├── agent_specs.yaml
│   └── task_requirements.md
├── resources/
│   ├── tools.json
│   └── dependencies.txt
├── workflows/
│   ├── standard_operating_procedures.md
│   └── collaboration_guidelines.md
└── templates/
    └── response_template.md
```

### Agent-Specific Extensions
Each agent type adds its division-specific files as outlined in the agent_initialization_files.md document.

## Context Integration

The system automatically integrates relevant context based on:

1. **Project Context**: Information from the specified project
2. **Task Context**: Details from the task description
3. **Organization Context**: Company-wide standards and procedures
4. **Dependency Context**: Related components and services

### Context Resolution Process
1. Parse project and task specifications
2. Match relevant organizational context
3. Identify related components and dependencies
4. Validate context consistency
5. Inject context into generated files

## Verification and Validation

### Pre-Creation Validation
- Verify agent type is valid
- Check project context availability
- Validate dependency requirements
- Ensure output directory permissions

### Post-Creation Verification
- Verify all required files were created
- Check file content validity
- Validate JSON/YAML syntax
- Confirm proper file permissions

## Error Handling

### Common Errors
- `AGENT_NOT_FOUND`: Specified agent type does not exist
- `PROJECT_NOT_FOUND`: Specified project context does not exist
- `INSUFFICIENT_CONTEXT`: Required context information is missing
- `PERMISSION_DENIED`: Insufficient permissions to create files
- `VALIDATION_ERROR`: Generated files fail validation

### Error Resolution
The system provides clear error messages with:
- Specific error type and description
- Steps to resolve the issue
- Alternative approaches when applicable

## Integration with Agent System

The generated files integrate seamlessly with:
- Agent command interface system
- Context management system  
- Response template system
- Super agent coordination patterns

## Configuration File Format

Custom configuration files use the following YAML format:

```yaml
agent:
  type: "backend-engineer"
  profile:
    name: "Custom Backend Engineer"
    capabilities: ["api-development", "database-design"]
  context:
    project: "my-project"
    task: "implement-authentication"
  output:
    directory: "./custom-output"
    exclude_common: false
  dependencies:
    include: true
    list: ["python", "postgresql", "fastapi"]
  specifications:
    custom_spec: "./custom-spec.yaml"
    template: "advanced"
```

## Extensibility

The system supports:
- Custom agent types through plugin system
- Custom project templates
- Extended file generators
- Integration with external systems

This CLI system provides a comprehensive solution for initializing agent-specific environments with all necessary context and resources for effective operation within the AICODE Labs ecosystem.