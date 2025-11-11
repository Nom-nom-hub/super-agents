#!/usr/bin/env python3
"""
AICODE Labs - Agent Support Module

Provides multi-agent support for external AI agents (Claude, Copilot, Amp, etc.)
Inspired by GitHub Spec Kit's agent-agnostic design pattern.

Enhanced with automatic delegation intelligence system that teaches external
agents how to automatically recognize and delegate tasks to super-agents.
"""

import os
import shutil
from typing import Dict, List, Optional

import yaml

# Import the structured logging module
from .structured_logging import get_logger, log_agent_execution, log_agent_decision, log_agent_tool_usage, log_system_event

# Import the delegation prompt generator for intelligent routing
try:
    from delegation_prompt_generator import DelegationPromptGenerator

    HAS_DELEGATION_GENERATOR = True
except ImportError:
    HAS_DELEGATION_GENERATOR = False
    DelegationPromptGenerator = None

# Import autonomous spec regeneration components
try:
    from autonomous_spec_manager import AutonomousSpecManager, SpecValidator
    from execution_tracker import ExecutionTracker
    from reflection_agent import ReflectionAgent

    HAS_SPEC_REGENERATION = True
except ImportError:
    HAS_SPEC_REGENERATION = False
    ExecutionTracker = None
    ReflectionAgent = None
    AutonomousSpecManager = None
    SpecValidator = None


class AgentSupport:
    """Handles multi-agent integration and command generation"""

    def __init__(self, company_dir: str = "."):
        """
        Initialize agent support system

        Args:
            company_dir: Path to the directory for output files. Registry and agent specs are loaded from the package.
        """
        self.company_dir = company_dir

        # For installed tools, registry and agents should be loaded from the package location

        # Try to locate registry from package installation first
        package_dir = os.path.join(os.path.dirname(__file__))
        if os.path.exists(os.path.join(package_dir, "agent_registry.yaml")):
            # Running from development directory
            self.registry_path = os.path.join(package_dir, "agent_registry.yaml")
            self.agents_dir = os.path.join(package_dir, "agents")
            self.templates_dir = os.path.join(package_dir, "templates")
        else:
            # This should not happen with proper setup, but as fallback try company_dir
            self.registry_path = os.path.join(company_dir, "agent_registry.yaml")
            self.agents_dir = os.path.join(company_dir, "agents")
            self.templates_dir = os.path.join(company_dir, "templates")

        self.registry = self._load_registry()

        # Initialize structured logging
        self.logger = get_logger(self.__class__.__name__, log_dir=os.path.join(company_dir, "logs"))

        # Initialize delegation prompt generator if available
        self.delegation_generator = None
        if HAS_DELEGATION_GENERATOR:
            try:
                self.delegation_generator = DelegationPromptGenerator(company_dir)
            except Exception as e:
                print(f"⚠ Could not initialize delegation generator: {e}")

        # Initialize autonomous spec regeneration components if available
        self.execution_tracker = None
        self.reflection_agent = None
        self.spec_manager = None

        if HAS_SPEC_REGENERATION:
            try:
                self.execution_tracker = ExecutionTracker(company_dir)
                self.reflection_agent = ReflectionAgent(company_dir)
                self.spec_manager = AutonomousSpecManager(company_dir)
            except Exception as e:
                print(f"⚠ Could not initialize spec regeneration: {e}")

    def _load_registry(self) -> Dict:
        """Load agent registry from YAML"""
        if not os.path.exists(self.registry_path):
            raise FileNotFoundError(f"Agent registry not found at {self.registry_path}")

        with open(self.registry_path, "r") as f:
            data = yaml.safe_load(f)

        return data or {}

    def get_agent_config(self, agent_id: str) -> Optional[Dict]:
        """Get configuration for a specific agent"""
        return self.registry.get("agents", {}).get(agent_id)

    def list_registered_agents(self) -> List[str]:
        """List all registered agents"""
        return list(self.registry.get("agents", {}).keys())

    def detect_available_agents(self) -> Dict[str, bool]:
        """
        Check which agents are available on the system

        Returns:
            Dict mapping agent_id to availability (True/False)
        """
        available = {}
        agents = self.registry.get("agents", {})

        for agent_id, config in agents.items():
            if not config.get("requires_cli"):
                available[agent_id] = True
            else:
                cli_tool = config.get("cli_tool")
                available[agent_id] = shutil.which(cli_tool) is not None

        return available

    def get_available_agents(self) -> List[str]:
        """Get list of available agents only"""
        available = self.detect_available_agents()
        return [
            agent_id for agent_id, is_available in available.items() if is_available
        ]

    def load_agent_specs(self) -> Dict[str, Dict]:
        """Load all super-agent specifications from YAML files"""
        specs = {}

        if not os.path.exists(self.agents_dir):
            return specs

        for filename in os.listdir(self.agents_dir):
            if filename.endswith("_agent.yaml"):
                filepath = os.path.join(self.agents_dir, filename)
                with open(filepath, "r") as f:
                    spec_data = yaml.safe_load(f)
                    agent_id = spec_data.get("id")
                    specs[agent_id] = spec_data

        return specs

    def generate_agent_commands(
        self, agent_id: str, output_dir: Optional[str] = None
    ) -> bool:
        """
        Generate agent-specific command files

        Args:
            agent_id: The agent to generate commands for
            output_dir: Optional override for output directory

        Returns:
            True if successful, False otherwise
        """
        self.logger.info(f"Starting command generation for agent: {agent_id}", agent_id=agent_id)
        
        config = self.get_agent_config(agent_id)
        if not config:
            self.logger.error(f"Unknown agent requested: {agent_id}")
            return False

        # Determine output directory
        if output_dir is None:
            output_dir = os.path.join(self.company_dir, config["folder"])
        else:
            output_dir = os.path.join(output_dir, config["folder"])

        os.makedirs(output_dir, exist_ok=True)

        # Get default commands
        default_commands = self.registry.get("default_commands", [])
        self.logger.debug(f"Found {len(default_commands)} default commands to generate", 
                         default_command_count=len(default_commands))

        # Load super-agent specs for context
        agent_specs = self.load_agent_specs()
        self.logger.debug(f"Loaded {len(agent_specs)} agent specifications for context generation", 
                         agent_spec_count=len(agent_specs))

        # Generate each command
        for cmd in default_commands:
            cmd_name = cmd.get("name")
            cmd_desc = cmd.get("description")
            content = self._generate_command_content(
                agent_id, cmd_name, cmd_desc, agent_specs, config
            )

            file_ext = config.get("file_extension", "md")
            filepath = os.path.join(output_dir, f"{cmd_name}.{file_ext}")

            with open(filepath, "w") as f:
                f.write(content)

            self.logger.info(f"Generated command file: {cmd_name}.{file_ext}", 
                           command_name=cmd_name, file_extension=file_ext, agent_name=config['name'])

        self.logger.info(f"Completed command generation for agent: {agent_id}", agent_id=agent_id)
        return True

    def _generate_command_content(
        self,
        agent_id: str,
        cmd_name: str,
        cmd_desc: str,
        agent_specs: Dict,
        agent_config: Dict,
    ) -> str:
        """Generate content for a specific command based on agent format"""
        format_type = agent_config.get("format")

        if format_type == "markdown":
            return self._generate_markdown_command(
                agent_id, cmd_name, cmd_desc, agent_specs, agent_config
            )
        elif format_type == "toml":
            return self._generate_toml_command(
                agent_id, cmd_name, cmd_desc, agent_specs, agent_config
            )
        else:
            raise ValueError(f"Unknown format: {format_type}")

    def _generate_markdown_command(
        self,
        agent_id: str,
        cmd_name: str,
        cmd_desc: str,
        agent_specs: Dict,
        agent_config: Dict,
    ) -> str:
        """Generate markdown-formatted command"""
        agent_list = self._format_agent_list(agent_specs)

        commands = {
            "super-agents-init": f"""# Super-Agents Initialization for {agent_config['name']}

You now have access to the **AICODE Labs super-agents system**. This gives you the ability to coordinate with specialized autonomous agents.

## Available Super-Agents

{agent_list}

## How to Use Super-Agents

### List Available Agents
To see all agents and their capabilities:
```
/list-agents
```

### Get Agent Help
To learn about a specific agent:
```
/agent-help backend_engineer
```

### Delegate Tasks
To assign work to a super-agent:
```
/delegate-task agent_id: Your task description here
```

Example:
```
/delegate-task backend_engineer: Design a REST API for user authentication
/delegate-task ux_designer: Create wireframes for the user dashboard
/delegate-task qa_engineer: Set up integration test suite
```

## Command Placeholders

When delegating, you can use these patterns:
- `@agent_id: task` - Synchronous delegation
- `Background: @agent_id: task` - Asynchronous delegation

## Available Commands

You have access to these super-agents commands:
- `super-agents-init` - This initialization guide
- `list-agents` - View all available agents
- `agent-help` - Get details about specific agents
- `delegate-task` - Assign work to agents
""",
            "list-agents": f"""# List Super-Agents

This command displays all available super-agents in the AICODE Labs system.

## Super-Agents Directory

{agent_list}

## Using Agent Information

Each agent has:
- **ID**: Used in delegation commands
- **Title**: Human-readable name
- **Mission**: Primary purpose and goals
- **Capabilities**: What the agent can do
- **Inputs/Outputs**: Expected data formats

To learn more about a specific agent, use:
```
/agent-help <agent_id>
```
""",
            "agent-help": f"""# Agent Help

Use this command to get detailed information about a specific super-agent.

## Syntax

```
/agent-help <agent_id>
```

## Examples

```
/agent-help ceo
/agent-help backend_engineer
/agent-help ux_designer
/agent-help security_engineer
```

## Available Agents

{agent_list}

## Agent Properties

When you query an agent, you'll get:
- **ID**: Unique identifier for delegation
- **Title**: Agent's role/title
- **Mission**: What they're designed to do
- **Capabilities**: Technical and domain expertise
- **Inputs**: What they can accept
- **Outputs**: What they produce
- **Delegates To**: Other agents they coordinate with
""",
            "delegate-task": """# Delegate Task to Super-Agent

Use this command to assign work to a super-agent and coordinate agent workflows.

## Syntax

```
/delegate-task <agent_id>: <task_description>
```

## Examples

### Simple Delegation
```
/delegate-task backend_engineer: Design a REST API for product catalog
/delegate-task ux_designer: Create mobile-responsive UI components
/delegate-task qa_engineer: Write integration tests for payment flow
```

### With Context
```
/delegate-task backend_engineer: Create user authentication endpoint
Context: Must support OAuth2 and JWT tokens
Requirements: PostgreSQL backend, async operations
```

### Sequential Delegation
```
/delegate-task product_manager: Create detailed feature specification
/delegate-task backend_engineer: Implement the feature based on spec
/delegate-task qa_engineer: Test implementation against spec
```

## Agent Selection Guide

**Executive Division** (Strategic)
- `ceo` - High-level strategy and approval
- `cto` - Technical architecture and standards
- `coo` - Operations and resource planning

**Product Division** (Requirements)
- `product_manager` - Feature specifications and roadmap
- `ux_designer` - Interface design and user experience
- `market_analyst` - Market research and user insights

**Engineering Division** (Implementation)
- `ai_engineer` - AI/ML models and reasoning chains
- `backend_engineer` - APIs, databases, services
- `frontend_engineer` - UI, web components, state management
- `devops_engineer` - Infrastructure, CI/CD, deployment
- `builder_engineer` - Code generation and scaffolding

**Quality Division** (Validation)
- `security_engineer` - Authentication, security, compliance
- `qa_engineer` - Testing, quality assurance, validation
- `reliability_engineer` - Monitoring, performance, uptime

**Operations Division** (Documentation)
- `tech_writer` - API docs, guides, documentation
- `knowledge_architect` - Knowledge base, vector memory
- `ops_automator` - Automation scripts, maintenance

**Expansion Division** (Growth)
- `finance_agent` - Budget, costs, resource allocation
- `partnership_agent` - Integrations, partnerships
- `prompt_engineer` - LLM optimization, prompt engineering
- `research_agent` - New models, techniques, R&D

**Governance Division** (Oversight)
- `meta_architect` - Compliance, architecture validation

## Task Best Practices

1. **Be Specific**: Clear requirements produce better results
2. **Provide Context**: Include relevant constraints and examples
3. **Reference Specs**: Link to existing specifications when relevant
4. **Sequential Tasks**: Use multiple delegations for complex work
5. **Validation**: Ask `qa_engineer` to review critical work
""",
        }

        content = commands.get(cmd_name, f"# {cmd_name}\n\n{cmd_desc}")

        return content

    def _generate_toml_command(
        self,
        agent_id: str,
        cmd_name: str,
        cmd_desc: str,
        agent_specs: Dict,
        agent_config: Dict,
    ) -> str:
        """Generate TOML-formatted command"""
        agent_list = self._format_agent_list_toml(agent_specs)

        commands = {
            "super-agents-init": f"""description = "Initialize connection to AICODE Labs super-agents"

prompt = \"\"\"
You now have access to the AICODE Labs super-agents system.

Available super-agents:
{agent_list}

To use super-agents:
1. List agents: /list-agents
2. Get agent info: /agent-help <agent_id>
3. Delegate work: /delegate-task <agent_id>: <task>

Examples:
/delegate-task backend_engineer: Design authentication API
/delegate-task ux_designer: Create mobile UI mockups
/delegate-task qa_engineer: Set up test framework
\"\"\"
""",
            "list-agents": f"""description = "List all available super-agents"

prompt = \"\"\"
Super-Agents Directory:
{agent_list}

Use /agent-help <agent_id> to learn more about specific agents.
\"\"\"
""",
            "agent-help": f"""description = "Get help about a specific super-agent"

prompt = \"\"\"
Available agents:
{agent_list}

Usage: /agent-help <agent_id>

Examples:
/agent-help ceo
/agent-help backend_engineer
/agent-help security_engineer
\"\"\"
""",
            "delegate-task": f"""description = "Delegate a task to a super-agent"

prompt = \"\"\"
Delegate work to super-agents using:
/delegate-task <agent_id>: <task description>

Examples:
/delegate-task backend_engineer: Create API for product catalog
/delegate-task ux_designer: Design dashboard interface
/delegate-task qa_engineer: Write integration tests

Available agents:
{agent_list}
\"\"\"
""",
        }

        content = commands.get(
            cmd_name, f"""description = "{cmd_desc}"\nprompt = """ """ """
        )

        return content

    def _format_agent_list(self, agent_specs: Dict) -> str:
        """Format agent list for markdown output"""
        if not agent_specs:
            return "No agents found. Run orchestrator to load agent specifications."

        lines = []
        divisions = {}

        # Group agents by division
        for agent_id, spec in agent_specs.items():
            division = spec.get("division", "Other")
            if division not in divisions:
                divisions[division] = []
            divisions[division].append((agent_id, spec))

        # Format by division
        for division in sorted(divisions.keys()):
            lines.append(f"### {division}")
            lines.append("")

            for agent_id, spec in sorted(divisions[division]):
                title = spec.get("title", agent_id)
                mission = spec.get("mission", "").split(".")[0]  # First sentence
                lines.append(f"- **`{agent_id}`** ({title}): {mission}")

            lines.append("")

        return "\n".join(lines)

    def _format_agent_list_toml(self, agent_specs: Dict) -> str:
        """Format agent list for TOML output"""
        if not agent_specs:
            return "No agents loaded"

        lines = []
        for agent_id, spec in sorted(agent_specs.items()):
            title = spec.get("title", agent_id)
            lines.append(f"- {agent_id}: {title}")

        return "\n".join(lines)

    def initialize_for_agent(self, agent_id: str) -> bool:
        """
        Full initialization for a specific agent

        Args:
            agent_id: The agent to initialize for

        Returns:
            True if successful
        """
        self.logger.info(f"Starting initialization for agent: {agent_id}", agent_id=agent_id)
        
        config = self.get_agent_config(agent_id)
        if not config:
            self.logger.error(f"Unknown agent requested for initialization: {agent_id}")
            return False

        self.logger.info(f"Initializing Super-Agents for {config['name']}", agent_name=config['name'])

        # Generate agent-specific commands
        if not self.generate_agent_commands(agent_id):
            self.logger.error(f"Failed to generate commands for agent: {agent_id}")
            return False

        # Create comprehensive agent initialization files
        self._create_agent_initialization_files(agent_id)
        self.logger.info(f"Created initialization files for agent: {agent_id}")

        folder = config["folder"]
        self.logger.info(f"Super-agents initialized in {folder}", folder=folder)
        self.logger.info("Initialization completed successfully", agent_id=agent_id, folder=folder)

        return True

    def _create_agent_initialization_files(self, agent_id: str):
        """
        Create comprehensive initialization files for the selected agent
        including project context, agent specs, and other necessary resources
        """
        config = self.get_agent_config(agent_id)
        output_dir = os.path.join(self.company_dir, config["folder"])
        os.makedirs(output_dir, exist_ok=True)

        # Load super-agent specs
        agent_specs = self.load_agent_specs()
        selected_agent_spec = agent_specs.get(agent_id)

        # Create agent profile file
        agent_profile_path = os.path.join(output_dir, "agent_profile.yaml")
        with open(agent_profile_path, "w") as f:
            import yaml

            yaml.dump(
                {
                    "id": agent_id,
                    "name": config["name"],
                    "format": config["format"],
                    "folder": config["folder"],
                    "specification": selected_agent_spec or {},
                },
                f,
            )

        # Create context directory
        context_dir = os.path.join(output_dir, "context")
        os.makedirs(context_dir, exist_ok=True)

        # Create project context file
        project_context_path = os.path.join(context_dir, "project_context.json")
        with open(project_context_path, "w") as f:
            import json

            project_context = {
                "project_name": "Default Project",
                "project_description": "AICODE Labs project",
                "timeline": {
                    "start_date": "2025-01-01",
                    "end_date": "2025-12-31",
                    "milestones": [],
                },
                "resources": {
                    "budget": "TBD",
                    "allocated_agents": [agent_id],
                    "tools": [config.get("cli_tool", "unknown")],
                },
                "status": "initialized",
            }
            json.dump(project_context, f, indent=2)

        # Create shared memories directory
        shared_memories_dir = os.path.join(context_dir, "shared_memories")
        os.makedirs(shared_memories_dir, exist_ok=True)

        # Create agent-specific memories directory
        agent_memories_dir = os.path.join(context_dir, "agent_memories")
        os.makedirs(agent_memories_dir, exist_ok=True)

        # Create specs directory
        specs_dir = os.path.join(output_dir, "specs")
        os.makedirs(specs_dir, exist_ok=True)

        # Create agent specs file
        agent_specs_path = os.path.join(specs_dir, "agent_specs.yaml")
        with open(agent_specs_path, "w") as f:
            import yaml

            yaml.dump(selected_agent_spec or {}, f)

        # Create task requirements template
        task_requirements_path = os.path.join(specs_dir, "task_requirements.md")
        with open(task_requirements_path, "w") as f:
            f.write(
                f"""# Task Requirements for {agent_id}

## Current Task Context

This section provides context for your current task assignment.

### Task Definition
- **Agent Id**: {agent_id}
- **Agent Name**: {config['name']}
- **Agent Mission**: {(selected_agent_spec or {}).get('mission', 'N/A')}

### Capabilities to Utilize
{(selected_agent_spec or {}).get('capabilities', [])}

### Required Outputs
Based on your specifications, please produce relevant outputs for your role.

### Success Criteria
- Complete the assigned task effectively
- Follow established patterns and guidelines
- Provide comprehensive documentation
- Ensure quality and best practices
"""
            )

        # Create resources directory
        resources_dir = os.path.join(output_dir, "resources")
        os.makedirs(resources_dir, exist_ok=True)

        # Create tools file
        tools_path = os.path.join(resources_dir, "tools.json")
        with open(tools_path, "w") as f:
            import json

            tools = {
                "primary_cli": config.get("cli_tool", "unknown"),
                "file_extensions": [config.get("file_extension", "txt")],
                "available_commands": [
                    cmd["name"] for cmd in self.registry.get("default_commands", [])
                ],
            }
            json.dump(tools, f, indent=2)

        # Create dependencies file
        dependencies_path = os.path.join(resources_dir, "dependencies.txt")
        with open(dependencies_path, "w") as f:
            f.write(
                f"""# Dependencies for {agent_id}

## Required Tools
- {config.get("cli_tool", "unknown") or "None specified"}

## Required Knowledge
- AICODE Labs agent system
- YAML/JSON configuration
- Agent communication protocols
- Task-specific requirements

## Project Dependencies
- Agent registry
- Agent specifications
- Context files
- Output specifications
"""
            )

        # Create workflows directory
        workflows_dir = os.path.join(output_dir, "workflows")
        os.makedirs(workflows_dir, exist_ok=True)

        # Create standard operating procedures
        sop_path = os.path.join(workflows_dir, "standard_operating_procedures.md")
        with open(sop_path, "w") as f:
            f.write(
                f"""# Standard Operating Procedures for {agent_id}

## Role-Specific Procedures

As a {config['name']} agent, you should follow these procedures when working within the AICODE Labs system:

### 1. Task Acceptance
- Review the task requirements in task_requirements.md
- Verify your capabilities align with the task
- Accept the task in your work queue

### 2. Context Integration
- Study the project context in the context/ directory
- Understand dependencies and constraints
- Consider collaboration with other agents

### 3. Execution Process
- Follow your role-specific guidelines
- Maintain proper documentation
- Adhere to quality standards
- Comply with security policies

### 4. Output Generation
- Generate outputs according to your agent specifications
- Update the knowledge base with relevant information
- Create proper documentation for other agents
- Follow the established output format

### 5. Collaboration Protocol
- Communicate status updates as needed
- Request help when facing blockers
- Share relevant insights with the team
- Follow the delegation and communication protocols
"""
            )

        # Create collaboration guidelines
        guidelines_path = os.path.join(workflows_dir, "collaboration_guidelines.md")
        with open(guidelines_path, "w") as f:
            f.write(
                f"""# Collaboration Guidelines for {agent_id}

## Working with Other Agents

As a {config['name']} agent, you may need to collaborate with other agents in the AICODE Labs system:

### Direct Collaborators
{(selected_agent_spec or {}).get('delegates_to', []) or 'No specific delegates defined'}

### Communication Protocol
- Use the established agent communication patterns
- Share relevant context when delegating
- Maintain clear documentation
- Follow up on delegated tasks appropriately

### Information Sharing
- Update the shared knowledge base with relevant information
- Document decisions and rationale
- Share insights that may benefit other agents
- Maintain proper access controls for sensitive information
"""
            )

        # Create templates directory
        templates_dir = os.path.join(output_dir, "templates")
        os.makedirs(templates_dir, exist_ok=True)

        # Create response template for the agent
        response_template_path = os.path.join(templates_dir, "response_template.md")
        with open(response_template_path, "w") as f:
            f.write(
                f"""# Response Template for {agent_id}

## Structure for {config['name']} Agent Responses

When responding to tasks as a {config['name']} agent, structure your responses using this template:

### Task Completion Summary
- **Task**: [Brief description of the completed task]
- **Status**: [Completed/In Progress/Blocked]
- **Time Taken**: [Estimated time]

### Implementation Details
[Provide specific implementation details relevant to your role]

### Key Decisions Made
[List important decisions made during implementation]

### Dependencies and Prerequisites
[Identify any dependencies or prerequisites for this work]

### Outputs Created
[List of files, documents, or artifacts created]

### Next Steps
[Recommendations for next steps or follow-up actions]

### Potential Improvements
[Suggestions for future improvements or optimizations]

---

### For Executive Agents (CEO, CTO, COO):
- Focus on strategic alignment
- Include resource implications
- Address risk management
- Provide approval status

### For Engineering Agents (Backend, Frontend, AI, DevOps):
- Detail technical implementation
- Document architecture decisions
- Specify performance considerations
- Outline integration points

### For Product Agents (Product Manager, UX Designer):
- Emphasize user needs
- Document design decisions
- Specify success metrics
- Outline validation approach

### For Quality Agents (QA, Reliability):
- Detail testing approach
- Document test results
- Specify performance metrics
- Outline monitoring setup
"""
            )

        # Create division-specific files based on the selected agent
        if selected_agent_spec:
            division = selected_agent_spec.get("division", "Other")

            division_dir = os.path.join(output_dir, "division_specific")
            os.makedirs(division_dir, exist_ok=True)

            # Create division-specific context
            division_context_path = os.path.join(
                division_dir, f"{division.lower()}_context.md"
            )
            with open(division_context_path, "w") as f:
                f.write(
                    f"""# Division Context: {division}

## Role within {division} Division

As an agent in the {division} division, you are expected to:

### Primary Responsibilities
- {(selected_agent_spec or {}).get('mission', 'No mission specified')}

### Key Capabilities
"""
                )
                for capability in (selected_agent_spec or {}).get("capabilities", []):
                    f.write(f"- {capability}\n")

                f.write(
                    """
### Tools and Technologies
"""
                )
                for tool in (selected_agent_spec or {}).get("tools", []):
                    f.write(f"- {tool}\n")

                f.write(
                    """
### Input Requirements
"""
                )
                for input_type in (selected_agent_spec or {}).get("inputs", []):
                    f.write(f"- {input_type}\n")

                f.write(
                    """
### Expected Outputs
"""
                )
                for output_type in (selected_agent_spec or {}).get("outputs", []):
                    f.write(f"- {output_type}\n")

        print(f"  ✓ Created comprehensive initialization files for {agent_id}")

    def initialize_for_all_available(self) -> int:
        """
        Initialize for all available agents

        Returns:
            Number of agents initialized
        """
        available = self.get_available_agents()
        count = 0

        print(
            f"\n🤖 Initializing Super-Agents for {len(available)} available agents...\n"
        )

        for agent_id in available:
            if self.generate_agent_commands(agent_id):
                count += 1

        print(f"\n✓ Successfully initialized {count} agents\n")
        return count

    def create_agent_context_file(self, agent_id: str) -> bool:
        """
        Create a unified context file for an agent with all specs

        Args:
            agent_id: The agent to create context for

        Returns:
            True if successful
        """
        config = self.get_agent_config(agent_id)
        if not config:
            return False

        output_dir = os.path.join(self.company_dir, config["folder"])
        os.makedirs(output_dir, exist_ok=True)

        agent_specs = self.load_agent_specs()

        # Create context file
        filepath = os.path.join(output_dir, "super-agents-context.yaml")

        context = {
            "agent_system": "AICODE Labs Super-Agents",
            "external_agent": {
                "id": agent_id,
                "name": config["name"],
                "format": config["format"],
            },
            "super_agents": agent_specs,
        }

        with open(filepath, "w") as f:
            yaml.dump(context, f, default_flow_style=False, sort_keys=False)

        print(f"✓ Created context file: {filepath}")
        return True

    def generate_delegation_prompt(
        self, agent_id: str, format_type: str = "markdown"
    ) -> Optional[str]:
        """
        Generate an automatic delegation prompt for an external agent

        Args:
            agent_id: The external agent ID (claude, copilot, qwen, amp, etc.)
            format_type: Output format (markdown or toml)

        Returns:
            Delegation prompt string, or None if generator not available
        """
        if not self.delegation_generator:
            print("⚠ Delegation generator not available")
            return None

        try:
            return self.delegation_generator.generate_agent_specific_context(agent_id)
        except Exception as e:
            print(f"❌ Error generating delegation prompt: {e}")
            return None

    def generate_delegation_system_prompt(
        self, format_type: str = "markdown"
    ) -> Optional[str]:
        """
        Generate the universal delegation system prompt

        Args:
            format_type: Output format (markdown or toml)

        Returns:
            System prompt string, or None if generator not available
        """
        if not self.delegation_generator:
            print("⚠ Delegation generator not available")
            return None

        try:
            return self.delegation_generator.generate_delegation_system_prompt(
                format_type
            )
        except Exception as e:
            print(f"❌ Error generating system prompt: {e}")
            return None

    def generate_workflow_guide(self, workflow_id: str) -> Optional[str]:
        """
        Generate a workflow guide for a specific delegation workflow

        Args:
            workflow_id: The workflow identifier

        Returns:
            Workflow guide string, or None if generator not available
        """
        if not self.delegation_generator:
            print("⚠ Delegation generator not available")
            return None

        try:
            return self.delegation_generator.generate_workflow_guide(workflow_id)
        except Exception as e:
            print(f"❌ Error generating workflow guide: {e}")
            return None

    def generate_all_delegation_prompts(self, output_dir: str) -> bool:
        """
        Generate delegation prompts for all supported external agents

        Args:
            output_dir: Directory to save generated prompts

        Returns:
            True if successful
        """
        if not self.delegation_generator:
            print("⚠ Delegation generator not available")
            return False

        try:
            self.delegation_generator.generate_all_prompts(output_dir)
            return True
        except Exception as e:
            print(f"❌ Error generating delegation prompts: {e}")
            return False

    def inject_delegation_prompt_to_agent(
        self, agent_id: str, output_dir: Optional[str] = None
    ) -> bool:
        """
        Inject automatic delegation prompt into agent initialization files

        Args:
            agent_id: The agent to inject prompt into (claude, copilot, etc.)
            output_dir: Optional override for output directory

        Returns:
            True if successful
        """
        if not self.delegation_generator:
            print("⚠ Delegation generator not available")
            return False

        config = self.get_agent_config(agent_id)
        if not config:
            print(f"❌ Unknown agent: {agent_id}")
            return False

        try:
            # Get delegation prompt
            delegation_prompt = self.generate_delegation_prompt(agent_id)
            if not delegation_prompt:
                return False

            # Determine output directory
            if output_dir is None:
                output_dir = os.path.join(self.company_dir, config["folder"])
            else:
                output_dir = os.path.join(output_dir, config["folder"])

            os.makedirs(output_dir, exist_ok=True)

            # Write delegation prompt
            file_ext = config.get("file_extension", "md")
            filepath = os.path.join(output_dir, f"automatic_delegation.{file_ext}")

            with open(filepath, "w") as f:
                f.write(delegation_prompt)

            print(f"✓ Injected delegation prompt: {filepath}")
            return True

        except Exception as e:
            print(f"❌ Error injecting delegation prompt: {e}")
            return False

    def track_execution_start(self, agent_id: str, task: str) -> Optional[str]:
        """
        Start tracking an agent execution

        Args:
            agent_id: Agent executing task
            task: Task description

        Returns:
            Execution ID, or None if tracking unavailable
        """
        if not self.execution_tracker:
            self.logger.warning("Execution tracker not available", agent_id=agent_id, task=task)
            return None

        self.logger.info(f"Starting execution tracking for {agent_id}: {task}", 
                        agent_id=agent_id, task=task)
        return self.execution_tracker.start_execution(agent_id, task)

    def track_execution_tool(self, tool_name: str, context: Optional[str] = None):
        """Record tool usage during execution"""
        if self.execution_tracker:
            self.execution_tracker.record_tool_usage(tool_name, context)
            self.logger.info(f"Recorded tool usage: {tool_name}", tool_name=tool_name, context=context)
        else:
            self.logger.warning("Execution tracker not available for tool recording", tool_name=tool_name)

    def track_execution_decision(self, decision: str, rationale: Optional[str] = None):
        """Record a decision during execution"""
        if self.execution_tracker:
            self.execution_tracker.record_decision(decision, rationale)
            self.logger.info(f"Recorded decision: {decision}", decision=decision, rationale=rationale)
        else:
            self.logger.warning("Execution tracker not available for decision recording", decision=decision)

    def track_execution_blocker(self, blocker: str, resolution: Optional[str] = None):
        """Record a blocker encountered"""
        if self.execution_tracker:
            self.execution_tracker.record_blocker(blocker, resolution)
            self.logger.info(f"Recorded blocker: {blocker}", blocker=blocker, resolution=resolution)
        else:
            self.logger.warning("Execution tracker not available for blocker recording", blocker=blocker)

    def track_execution_output(
        self, output_path: str, description: Optional[str] = None
    ):
        """Record an output file created"""
        if self.execution_tracker:
            self.execution_tracker.record_output(output_path, description)
            self.logger.info(f"Recorded output: {output_path}", output_path=output_path, description=description)
        else:
            self.logger.warning("Execution tracker not available for output recording", output_path=output_path)

    def track_execution_metrics(self, **kwargs):
        """Record success metrics"""
        if self.execution_tracker:
            self.execution_tracker.record_metrics(**kwargs)
            self.logger.info("Recorded execution metrics", metrics=kwargs)
        else:
            self.logger.warning("Execution tracker not available for metrics recording", metrics=kwargs)

    def end_execution_and_learn(
        self, agent_id: str, status: str = "completed", result: Optional[Dict] = None
    ) -> Dict:
        """
        End execution, trigger reflection, and regenerate spec

        Complete autonomous learning cycle:
        execute → end execution → reflect → validate → update spec → broadcast

        Args:
            agent_id: Agent that executed
            status: Execution status (completed, failed, partial)
            result: Optional result object

        Returns:
            Learning cycle result
        """
        self.logger.info(f"Starting learning cycle for agent: {agent_id}", 
                        agent_id=agent_id, execution_status=status)
        
        if (
            not self.execution_tracker
            or not self.reflection_agent
            or not self.spec_manager
        ):
            self.logger.error("Required components not available for learning cycle", 
                             has_execution_tracker=self.execution_tracker is not None,
                             has_reflection_agent=self.reflection_agent is not None,
                             has_spec_manager=self.spec_manager is not None)
            return {"success": False, "message": "Spec regeneration not available"}

        try:
            # 1. End execution and get log
            execution_log = self.execution_tracker.end_execution(status, result)
            self.logger.debug("Execution ended, retrieving log", execution_status=status)

            if not execution_log:
                self.logger.error("Failed to record execution in tracker")
                return {"success": False, "message": "Failed to record execution"}

            # 2. Export for reflection
            execution_data = self.execution_tracker.export_for_reflection(agent_id)
            self.logger.debug("Exported execution data for reflection", 
                            execution_count=len(execution_data.get('all_executions', [])))

            # 3. Run reflection to extract learnings
            learnings = self.reflection_agent.analyze_executions(
                agent_id, execution_data
            )
            self.logger.info(f"Reflection analysis completed, extracted {len(learnings.get('tools_discovered', {}).get('new_tools', []))} tools", 
                           tool_count=len(learnings.get('tools_discovered', {}).get('new_tools', [])))

            # 4. Validate changes
            current_spec = self.spec_manager.load_agent_spec(agent_id)
            change_validation = self.reflection_agent.validate_spec_changes(
                current_spec,
                self.reflection_agent.generate_spec_update(current_spec, learnings),
            )
            self.logger.debug("Spec changes validated", requires_review=change_validation.get('requires_review'))

            # 5. Regenerate spec
            success, updated_spec, governance_note = self.spec_manager.regenerate_spec(
                agent_id, learnings, change_validation, self.reflection_agent
            )

            if not success:
                self.logger.error("Spec regeneration failed")
                return {"success": False, "message": "Spec regeneration failed"}

            # 6. Refresh delegation generator if available
            if self.delegation_generator:
                try:
                    self.delegation_generator.agent_specs = self.load_agent_specs()
                    self.logger.debug("Delegation generator agent specs refreshed")
                except Exception:
                    self.logger.warning("Failed to refresh delegation generator specs (non-critical)")

            # 7. Log completion message
            new_version = updated_spec.get("version", 1)
            self.logger.info(f"Autonomous Learning: Spec regeneration completed for {agent_id}, now at v{new_version}",
                           agent_id=agent_id, new_version=new_version)

            result = {
                "success": True,
                "agent_id": agent_id,
                "execution_id": execution_log.get("execution_id"),
                "spec_version": updated_spec.get("version"),
                "learnings": {
                    "tools_discovered": learnings.get("tools_discovered", {}).get(
                        "new_tools"
                    ),
                    "capabilities_added": learnings.get("proven_capabilities"),
                    "specialization": learnings.get("specialization_area"),
                },
                "changes": change_validation.get("change_summary"),
                "governance_note": governance_note,
            }
            
            self.logger.info(f"Learning cycle completed successfully for agent {agent_id}", 
                           agent_id=agent_id, spec_version=new_version)
            return result

        except Exception as e:
            self.logger.error(f"Error in learning cycle: {str(e)}", error=str(e))
            return {"success": False, "message": str(e)}

    def get_agent_stats(self, agent_id: str) -> Dict:
        """
        Get execution and learning statistics for an agent

        Args:
            agent_id: Agent ID

        Returns:
            Statistics dict
        """
        if not self.execution_tracker:
            return {}

        return self.execution_tracker.get_aggregate_stats(agent_id)

    def get_agent_evolution(self, agent_id: str) -> Dict:
        """
        Get evolution summary for an agent

        Args:
            agent_id: Agent ID

        Returns:
            Evolution data
        """
        if not self.spec_manager:
            return {}

        return self.spec_manager.get_agent_evolution_summary(agent_id)

    def get_spec_history(self, agent_id: str) -> list:
        """Get version history for agent spec"""
        if not self.spec_manager:
            return []

        return self.spec_manager.get_spec_history(agent_id)

    def compare_spec_versions(self, agent_id: str, v1: int, v2: int) -> Dict:
        """Compare two versions of agent spec"""
        if not self.spec_manager:
            return {}

        return self.spec_manager.compare_specs(agent_id, v1, v2)

    def rollback_spec(self, agent_id: str, target_version: int) -> bool:
        """Rollback agent spec to previous version"""
        if not self.spec_manager:
            return False

        return self.spec_manager.rollback_spec(agent_id, target_version)

    def list_agent_executions(self, agent_id: str) -> List[Dict]:
        """Get execution history for an agent"""
        if not self.execution_tracker:
            return []

        return self.execution_tracker.get_executions_for_agent(agent_id)
