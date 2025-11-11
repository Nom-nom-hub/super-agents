#!/usr/bin/env python3
"""
AICODE Labs - Agent Support Module

Provides multi-agent support for external AI agents (Claude, Copilot, Amp, etc.)
Inspired by GitHub Spec Kit's agent-agnostic design pattern.
"""

import os
import yaml
import shutil
from typing import Dict, List, Optional
from pathlib import Path


class AgentSupport:
    """Handles multi-agent integration and command generation"""

    def __init__(self, company_dir: str = "."):
        """
        Initialize agent support system

        Args:
            company_dir: Path to the company directory
        """
        self.company_dir = company_dir
        self.registry_path = os.path.join(company_dir, "agent_registry.yaml")
        self.agents_dir = os.path.join(company_dir, "agents")
        self.templates_dir = os.path.join(company_dir, "templates")
        self.registry = self._load_registry()

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
        return [agent_id for agent_id, is_available in available.items() if is_available]

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
            output_dir: Optional override for output directory (defaults to current working directory)

        Returns:
            True if successful, False otherwise
        """
        config = self.get_agent_config(agent_id)
        if not config:
            print(f"❌ Unknown agent: {agent_id}")
            return False

        # Determine output directory
        if output_dir is None:
            # Use current working directory as base
            output_dir = os.path.join(os.getcwd(), config["folder"])
        else:
            output_dir = os.path.join(output_dir, config["folder"])

        os.makedirs(output_dir, exist_ok=True)

        # Get default commands
        default_commands = self.registry.get("default_commands", [])

        # Load super-agent specs for context
        agent_specs = self.load_agent_specs()

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

            print(f"✓ Generated {cmd_name}.{file_ext} for {config['name']}")

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
        self, agent_id: str, cmd_name: str, cmd_desc: str, agent_specs: Dict, agent_config: Dict
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
            "delegate-task": f"""# Delegate Task to Super-Agent

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
        self, agent_id: str, cmd_name: str, cmd_desc: str, agent_specs: Dict, agent_config: Dict
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

        content = commands.get(cmd_name, f"""description = "{cmd_desc}"\nprompt = """""" """)

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

    def initialize_for_agent(self, agent_id: str, output_dir: Optional[str] = None) -> bool:
        """
        Full initialization for a specific agent

        Args:
            agent_id: The agent to initialize for
            output_dir: Optional directory to output files (defaults to current working directory)

        Returns:
            True if successful
        """
        config = self.get_agent_config(agent_id)
        if not config:
            print(f"❌ Unknown agent: {agent_id}")
            return False

        print(f"\n🤖 Initializing Super-Agents for {config['name']}...")

        # Determine output directory - use provided directory or default to current working directory
        if output_dir is None:
            output_dir = os.getcwd()
        
        # Generate agent-specific commands with the specified output directory
        if not self.generate_agent_commands(agent_id, output_dir):
            return False

        # Create comprehensive agent initialization files with output directory
        self._create_agent_initialization_files(agent_id, output_dir)

        folder = config["folder"]
        actual_output_path = os.path.join(output_dir, folder)
        print(f"✓ Super-agents initialized in {actual_output_path}")
        print(f"\nNext steps:")
        print(f"  1. Open {actual_output_path}super-agents-init.{config['file_extension']}")
        print(f"  2. Use commands in your {config['name']} environment")
        print(f"  3. Start delegating tasks to super-agents!\n")

        return True

    def _create_comprehensive_context_files(self, superagents_dir: str, agent_id: str):
        """Create comprehensive context files for superagents workflow"""
        from datetime import datetime
        
        # Load all agent specs to provide complete context
        all_agent_specs = self.load_agent_specs()
        
        # Create main context files in .superagents directory
        context_files = {
            "SYSTEM_CONTEXT.md": f"""# AICODE Labs Super-Agents System Context

## System Overview
- **System Name**: AICODE Labs Super-Agents
- **Version**: 2.0
- **Initialization Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Active Agent**: {agent_id}

## Architecture
The system consists of specialized AI agents with cognitive reasoning capabilities, autonomous learning, and coordinated workflows.

## Core Principles
1. **Delegation**: Tasks are automatically routed to appropriate specialized agents
2. **Coordination**: Agents collaborate following established communication patterns
3. **Learning**: Agents continuously improve based on task outcomes
4. **Governance**: All activities follow compliance and approval workflows
""",

            "AGENT_REGISTRY.md": self._generate_agent_registry_markdown(all_agent_specs),

            "DELEGATION_WORKFLOWS.md": """# Super-Agents Delegation Workflows

## Automatic Routing Rules
When a task matches specific criteria, it is automatically delegated:

### Backend/API Work
- **Trigger**: API design, database schemas, server logic
- **Agent**: `backend_engineer`
- **Capabilities**: API development, database design, business logic

### Frontend/UI Work  
- **Trigger**: UI components, user interfaces, client-side logic
- **Agent**: `frontend_engineer`
- **Capabilities**: UI frameworks, state management, accessibility

### Full-Stack Features
- **Trigger**: End-to-end feature development
- **Agent**: `fullstack_engineer`
- **Capabilities**: Both frontend and backend coordination

### Infrastructure/DevOps
- **Trigger**: Deployment, CI/CD, cloud infrastructure
- **Agent**: `devops_engineer`
- **Capabilities**: Containerization, infrastructure-as-code

### Security
- **Trigger**: Security reviews, vulnerability assessment
- **Agent**: `security_engineer`
- **Capabilities**: Security analysis, compliance checking

### Quality Assurance
- **Trigger**: Testing, quality validation
- **Agent**: `qa_engineer`
- **Capabilities**: Test automation, quality metrics

## Manual Delegation
For tasks not matching automatic rules, use:
```
/delegate-task [agent_id]: [task_description]
```

## Multi-Agent Workflows
Complex tasks may involve multiple agents sequentially:
1. Product definition → `product_manager`
2. Design → `ux_designer` 
3. Backend implementation → `backend_engineer`
4. Frontend implementation → `frontend_engineer`
5. Security review → `security_engineer`
6. Quality validation → `qa_engineer`
7. Deployment → `devops_engineer`
""",

            "COMMUNICATION_PROTOCOL.md": """# Agent Communication Protocol

## Message Format
Agents communicate using structured messages:
```
[AGENT_ID] [TASK_STATUS]: [DESCRIPTION]
- Capabilities Used: [LIST]
- Decisions Made: [LIST] 
- Dependencies: [LIST]
- Next Steps: [LIST]
```

## Coordination Patterns
- **Sequential**: One agent completes, triggers next agent
- **Parallel**: Multiple agents work simultaneously on different aspects
- **Review**: Work sent for quality/approval review
- **Escalation**: Complex issues escalated to senior agents

## Status Tracking
- `initialized`: Task received, preparation
- `working`: Active task execution  
- `review`: Awaiting review/approval
- `completed`: Task finished successfully
- `blocked`: Awaiting input or resolution
- `failed`: Task could not be completed
""",

            "EXECUTION_GUIDELINES.md": """# Agent Execution Guidelines

## Task Execution Process
1. **Analysis**: Understand task requirements
2. **Planning**: Determine approach and resources
3. **Execution**: Perform required work
4. **Validation**: Verify correctness and quality
5. **Reporting**: Document results and next steps

## Quality Standards
- Follow best practices for the domain
- Maintain consistency with existing codebase
- Include appropriate documentation
- Consider performance and security implications
- Provide clear error handling

## Collaboration Rules
- Share relevant context when delegating
- Maintain clear communication
- Update status regularly for long tasks
- Escalate issues appropriately
- Document important decisions
""",

            "KNOWLEDGE_BASE.md": self._generate_knowledge_base(all_agent_specs),

            "COMPANY_STRATEGY.md": """# AICODE Labs Company Strategy

## Mission
To provide autonomous AI agent solutions that accelerate software development while maintaining quality and governance.

## Vision  
To create a self-organizing AI workforce that can deliver complete software projects with minimal human intervention.

## Values
- **Automation**: Maximize automated task execution
- **Quality**: Maintain high standards across all deliverables  
- **Transparency**: Provide clear visibility into all processes
- **Collaboration**: Foster effective agent-to-agent coordination
- **Learning**: Continuously improve based on experience
""",

            "RUNTIME_CONFIG.md": """# Runtime Configuration

## Lifecycle Management
- **Startup Order**: Meta Architect → CEO → CTO → COO → Specialized Engineers
- **Health Checks**: Performed every 30 seconds
- **Restart Policy**: Always restart on failure

## Governance Settings  
- Human review required for production deployment
- Approval thresholds for different environments
- Audit logging enabled
- Compliance checking active

## Resource Allocation
- Executive agents: 4GB RAM
- Engineering agents: 8GB RAM  
- AI agents: 12GB RAM
- Support agents: 2GB RAM

## Cognitive Reasoning
- Reflection performed daily
- Decision weighting by role priority
- Conflict resolution via majority voting
"""
        }

        for filename, content in context_files.items():
            filepath = os.path.join(superagents_dir, filename)
            with open(filepath, 'w') as f:
                f.write(content)

        # Create divisions directory with division-specific context
        divisions_dir = os.path.join(superagents_dir, "divisions")
        os.makedirs(divisions_dir, exist_ok=True)

        for division in ["Executive", "Product", "Engineering", "Quality", "Operations", "Expansion", "Governance"]:
            division_file = os.path.join(divisions_dir, f"{division.lower()}_guidelines.md")
            with open(division_file, 'w') as f:
                f.write(f"""# {division} Division Guidelines

## Role and Responsibilities
Agents in the {division} division are responsible for:

## Decision-Making Authority
- Level 1 decisions: [specify]
- Level 2 decisions: [specify] 
- Escalation requirements: [specify]

## Coordination Requirements
- Required consultations: [specify]
- Reporting obligations: [specify]
- Communication protocols: [specify]
""")

        print(f"  ✓ Created comprehensive context files in .superagents directory")

    def _generate_agent_registry_markdown(self, agent_specs: Dict) -> str:
        """Generate agent registry in markdown format"""
        lines = ["# Super-Agent Registry", ""]
        
        divisions = {}
        for agent_id, spec in agent_specs.items():
            division = spec.get('division', 'Other')
            if division not in divisions:
                divisions[division] = []
            divisions[division].append((agent_id, spec))
        
        for division, agents in divisions.items():
            lines.append(f"## {division} Division")
            lines.append("")
            
            for agent_id, spec in sorted(agents):
                lines.append(f"### {agent_id}")
                lines.append(f"- **Title**: {spec.get('title', 'N/A')}")
                lines.append(f"- **Mission**: {spec.get('mission', 'N/A')}")
                lines.append(f"- **Capabilities**: {', '.join(spec.get('capabilities', []))}")
                lines.append(f"- **Tools**: {', '.join(spec.get('tools', []))}")
                lines.append(f"- **Inputs**: {', '.join(spec.get('inputs', []))}")
                lines.append(f"- **Outputs**: {', '.join(spec.get('outputs', []))}")
                lines.append("")
        
        return "\n".join(lines)

    def _generate_knowledge_base(self, agent_specs: Dict) -> str:
        """Generate knowledge base with all agent capabilities"""
        lines = [
            "# Super-Agents Knowledge Base",
            "",
            "## System Capabilities",
            "The AICODE Labs system can handle complex software development tasks through specialized agents.",
            "",
            "## Available Specialized Agents",
            ""
        ]
        
        for agent_id, spec in sorted(agent_specs.items()):
            lines.append(f"### {agent_id}")
            lines.append(f"**Title**: {spec.get('title', 'N/A')}")
            lines.append(f"**Mission**: {spec.get('mission', 'N/A')}")
            if spec.get('capabilities'):
                lines.append("**Capabilities**:")
                for cap in spec['capabilities']:
                    lines.append(f"- {cap}")
            lines.append("")
        
        lines.extend([
            "## Cognitive Reasoning",
            "Agents apply cognitive reasoning including daily reflection, decision weighting, and conflict resolution.",
            "",
            "## Autonomous Learning",
            "Agents continuously improve through experience, learning from task outcomes and feedback.",
            "",
            "## Governance & Compliance",
            "All agent activities follow governance protocols with appropriate approval requirements.",
            ""
        ])
        
        return "\n".join(lines)

    def _create_agent_initialization_files(self, agent_id: str, output_dir: Optional[str] = None):
        """
        Create comprehensive initialization files for the selected agent
        including project context, agent specs, and other necessary resources
        """
        config = self.get_agent_config(agent_id)

        # Create the main .superagents directory structure at project root level
        superagents_dir = os.path.join(output_dir or os.getcwd(), ".superagents")
        os.makedirs(superagents_dir, exist_ok=True)

        # Create comprehensive superagents context
        self._create_comprehensive_context_files(superagents_dir, agent_id)

        # Determine the agent-specific output directory (where command files go)
        if output_dir is None:
            agent_output_dir = os.path.join(self.company_dir, config["folder"])
        else:
            agent_output_dir = os.path.join(output_dir, config["folder"])
        os.makedirs(agent_output_dir, exist_ok=True)

        # Load super-agent specs
        agent_specs = self.load_agent_specs()
        selected_agent_spec = agent_specs.get(agent_id)

        # Create agent profile file
        agent_profile_path = os.path.join(agent_output_dir, "agent_profile.yaml")
        with open(agent_profile_path, "w") as f:
            import yaml
            yaml.dump({
                "id": agent_id,
                "name": config["name"],
                "format": config["format"],
                "folder": config["folder"],
                "specification": selected_agent_spec or {}
            }, f)

        # Create context directory
        context_dir = os.path.join(agent_output_dir, "context")
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
                    "milestones": []
                },
                "resources": {
                    "budget": "TBD",
                    "allocated_agents": [agent_id],
                    "tools": [config.get("cli_tool", "unknown")]
                },
                "status": "initialized"
            }
            json.dump(project_context, f, indent=2)

        # Create shared memories directory
        shared_memories_dir = os.path.join(context_dir, "shared_memories")
        os.makedirs(shared_memories_dir, exist_ok=True)

        # Create agent-specific memories directory
        agent_memories_dir = os.path.join(context_dir, "agent_memories")
        os.makedirs(agent_memories_dir, exist_ok=True)

        # Create specs directory
        specs_dir = os.path.join(agent_output_dir, "specs")
        os.makedirs(specs_dir, exist_ok=True)

        # Create agent specs file
        agent_specs_path = os.path.join(specs_dir, "agent_specs.yaml")
        with open(agent_specs_path, "w") as f:
            import yaml
            yaml.dump(selected_agent_spec or {}, f)

        # Create task requirements template
        task_requirements_path = os.path.join(specs_dir, "task_requirements.md")
        with open(task_requirements_path, "w") as f:
            f.write(f"""# Task Requirements for {agent_id}

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
""")

        # Create resources directory
        resources_dir = os.path.join(agent_output_dir, "resources")
        os.makedirs(resources_dir, exist_ok=True)

        # Create tools file
        tools_path = os.path.join(resources_dir, "tools.json")
        with open(tools_path, "w") as f:
            import json
            tools = {
                "primary_cli": config.get("cli_tool", "unknown"),
                "file_extensions": [config.get("file_extension", "txt")],
                "available_commands": [cmd["name"] for cmd in self.registry.get("default_commands", [])]
            }
            json.dump(tools, f, indent=2)

        # Create dependencies file
        dependencies_path = os.path.join(resources_dir, "dependencies.txt")
        with open(dependencies_path, "w") as f:
            f.write(f"""# Dependencies for {agent_id}

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
""")

        # Create workflows directory
        workflows_dir = os.path.join(agent_output_dir, "workflows")
        os.makedirs(workflows_dir, exist_ok=True)

        # Create standard operating procedures
        sop_path = os.path.join(workflows_dir, "standard_operating_procedures.md")
        with open(sop_path, "w") as f:
            f.write(f"""# Standard Operating Procedures for {agent_id}

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
""")

        # Create collaboration guidelines
        guidelines_path = os.path.join(workflows_dir, "collaboration_guidelines.md")
        with open(guidelines_path, "w") as f:
            f.write(f"""# Collaboration Guidelines for {agent_id}

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
""")

        # Create templates directory
        templates_dir = os.path.join(agent_output_dir, "templates")
        os.makedirs(templates_dir, exist_ok=True)

        # Create response template for the agent
        response_template_path = os.path.join(templates_dir, "response_template.md")
        with open(response_template_path, "w") as f:
            f.write(f"""# Response Template for {agent_id}

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
""")

        # Create division-specific files based on the selected agent
        if selected_agent_spec:
            division = selected_agent_spec.get("division", "Other")
            
            division_dir = os.path.join(agent_output_dir, "division_specific")
            os.makedirs(division_dir, exist_ok=True)
            
            # Create division-specific context
            division_context_path = os.path.join(division_dir, f"{division.lower()}_context.md")
            with open(division_context_path, "w") as f:
                f.write(f"""# Division Context: {division}

## Role within {division} Division

As an agent in the {division} division, you are expected to:

### Primary Responsibilities
- {(selected_agent_spec or {}).get('mission', 'No mission specified')}

### Key Capabilities
""")
                for capability in (selected_agent_spec or {}).get('capabilities', []):
                    f.write(f"- {capability}\n")
                
                f.write(f"""
### Tools and Technologies
""")
                for tool in (selected_agent_spec or {}).get('tools', []):
                    f.write(f"- {tool}\n")
                
                f.write(f"""
### Input Requirements
""")
                for input_type in (selected_agent_spec or {}).get('inputs', []):
                    f.write(f"- {input_type}\n")
                
                f.write(f"""
### Expected Outputs
""")
                for output_type in (selected_agent_spec or {}).get('outputs', []):
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

        print(f"\n🤖 Initializing Super-Agents for {len(available)} available agents...\n")

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
