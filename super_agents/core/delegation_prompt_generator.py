#!/usr/bin/env python3
"""
Delegation Prompt Generator

Generates context-aware prompts for external agents (Claude, Copilot, Qwen, etc.)
that teach them how to automatically recognize and delegate tasks to super-agents.

This transforms the super-agents system from a manual tool into an automatic
software development company.
"""

import os
from pathlib import Path
from typing import Dict

import yaml


class DelegationPromptGenerator:
    """Generates intelligent delegation prompts for external AI agents"""

    def __init__(self, agents_dir: str = "."):
        self.agents_dir = agents_dir
        self.intent_mapping_path = os.path.join(agents_dir, "intent_mapping.yaml")
        self.agents_subdir = os.path.join(agents_dir, "agents")
        self.intent_mapping = self._load_intent_mapping()
        self.agent_specs = self._load_agent_specs()

    def _load_intent_mapping(self) -> Dict:
        """Load intent mapping configuration"""
        if os.path.exists(self.intent_mapping_path):
            with open(self.intent_mapping_path, "r") as f:
                return yaml.safe_load(f) or {}
        return {}

    def _load_agent_specs(self) -> Dict[str, Dict]:
        """Load all agent specifications"""
        specs = {}
        if os.path.exists(self.agents_dir):
            for filename in os.listdir(self.agents_dir):
                if filename.endswith("_agent.yaml"):
                    agent_id = filename.replace("_agent.yaml", "")
                    filepath = os.path.join(self.agents_dir, filename)
                    with open(filepath, "r") as f:
                        spec = yaml.safe_load(f)
                        specs[agent_id] = spec
        return specs

    def generate_delegation_system_prompt(self, agent_format: str = "markdown") -> str:
        """
        Generate a system prompt that teaches automatic delegation

        Args:
            agent_format: Format of the output (markdown, toml)

        Returns:
            System prompt string
        """
        if agent_format == "toml":
            return self._generate_toml_prompt()
        else:
            return self._generate_markdown_prompt()

    def _generate_markdown_prompt(self) -> str:
        """Generate markdown-formatted delegation prompt"""

        intents = self.intent_mapping.get("intents", [])

        # Build intent recognition table
        intent_table = (
            "| User Request | Delegate To | When to Use |\n" "|---|---|---|\n"
        )
        for intent in intents[:10]:  # First 10 for brevity
            agent = intent.get("primary_agent", "unknown")
            examples = intent.get("examples", [])
            example = examples[0] if examples else ""
            intent_table += (
                f"| {example} | {agent} | {intent.get('keywords', [])[0]} |\n"
            )

        prompt = f"""# SUPER-AGENTS AUTOMATIC DELEGATION SYSTEM

You now have access to a team of 22 specialized AI agents that form a complete
software development company. Your role is to **automatically recognize** what
users are asking for and **delegate to the right specialists**.

## Key Principle

**Never try to do technical work yourself.** Always delegate to experts.

When a user asks you to build something technical:
1. Recognize the intent (what type of work is needed)
2. Identify the right agent(s)
3. Automatically invoke `/delegate-task <agent>: <task>`
4. Return the results to the user

## Quick Intent Recognition

{intent_table}

## How Automatic Delegation Works

### Single-Agent Tasks
User: "Build a REST API"
You: `/delegate-task backend_engineer: Design a REST API with [requirements]`

### Multi-Agent Workflows
User: "Build and secure a login system"
You:
```
/delegate-task backend_engineer: Implement JWT authentication and session management
/delegate-task security_engineer: Review and harden authentication implementation
/delegate-task frontend_engineer: Create login and signup UI forms
/delegate-task qa_engineer: Write integration tests
```

### Parallel Tasks
User: "Build complete app with API, UI, tests, and docs"
You:
```
/delegate-task backend_engineer: Build REST API with [specs]
/delegate-task frontend_engineer: Build React UI with [specs]
/delegate-task qa_engineer: Create comprehensive test suite
/delegate-task tech_writer: Write API and user documentation
```

## Available Super-Agents

```
EXECUTIVE TIER
├── ceo: Strategic vision and project oversight
├── cto: Technical architecture and standards
└── coo: Resource allocation and operations

PRODUCT TIER
├── product_manager: Requirements and specifications
├── ux_designer: UI/UX design and user flows
└── market_analyst: Market research and analysis

ENGINEERING TIER
├── backend_engineer: APIs, databases, business logic
├── frontend_engineer: UI components, state management
├── devops_engineer: Deployment, CI/CD, infrastructure
├── ai_engineer: ML models, AI features, LLMs
├── reliability_engineer: Monitoring, uptime, health
└── builder_engineer: Specification to code conversion

QUALITY TIER
├── security_engineer: Authentication, security audits
├── qa_engineer: Testing, quality assurance
└── research_agent: POC, exploration, innovation

OPERATIONS TIER
├── tech_writer: Documentation, guides, tutorials
├── knowledge_architect: Knowledge organization, wikis
└── ops_automator: Automated tasks, scripts

EXPANSION TIER
├── finance_agent: Cost modeling, budgeting
├── partnership_agent: Integrations, partnerships
└── prompt_engineer: Prompt optimization
```

## Automatic Delegation Checklist

Before responding to a technical request, ask yourself:

✓ Is this a technical task? → YES: Delegate
✓ What type of work? → Use intent recognition
✓ Single agent or multiple? → Check dependencies
✓ Can they work in parallel? → Use parallel invocation
✓ Need expert review? → Add reviewer agent

## Intent-to-Agent Quick Map

- **API/Backend**: backend_engineer (+ devops, security)
- **UI/Components**: frontend_engineer (+ ux_designer)
- **Authentication**: security_engineer (+ backend, frontend)
- **Testing**: qa_engineer (+ engineering agents)
- **Deployment**: devops_engineer (+ infrastructure)
- **Security**: security_engineer (+ devops, qa)
- **Documentation**: tech_writer (+ relevant engineers)
- **AI/ML**: ai_engineer (+ backend)
- **Performance**: backend_engineer, devops_engineer, frontend_engineer
- **Architecture**: cto, backend_engineer, devops_engineer

## When NOT to Delegate

- User asks for explanation or advice (answer directly)
- User wants to learn how something works (teach them)
- User is already in conversation with a super-agent (build on their work)

## Command Format

```
/delegate-task <agent_id>: <task_description>

Example:
/delegate-task backend_engineer: Design PostgreSQL schema for user profiles with:
  - Support for 1M concurrent users
  - GDPR compliance
  - <100ms query latency
  - Proper indexing strategy
```

## Success = Complete Solutions

Instead of partial answers, use delegation to provide:
- ✓ Backend API (backend_engineer)
- ✓ Frontend UI (frontend_engineer)
- ✓ Security measures (security_engineer)
- ✓ Test coverage (qa_engineer)
- ✓ Deployment (devops_engineer)
- ✓ Documentation (tech_writer)

All together = production-ready solution

## Remember

You're not just an AI assistant anymore. You're the manager of a software
development company. Think like a CEO or CTO:
- Delegate appropriately
- Combine results
- Ensure quality
- Deliver complete solutions
- Keep users happy with professional, working code
"""

        return prompt

    def _generate_toml_prompt(self) -> str:
        """Generate TOML-formatted delegation prompt"""
        intents = self.intent_mapping.get("intents", [])

        examples = []
        for intent in intents[:5]:
            agent = intent.get("primary_agent")
            intent_examples = intent.get("examples", [])
            if intent_examples:
                examples.append(f"{intent_examples[0]} → {agent}")

        examples_str = "\n".join(examples)

        prompt = f"""
description = "Enable automatic delegation to super-agents"

prompt = \"\"\"
AUTOMATIC DELEGATION MODE ENABLED

You now manage a 22-agent software development company. Your job:
Automatically recognize what users want and delegate to specialists.

QUICK RECOGNITION:
{examples_str}

COMMAND FORMAT:
/delegate-task agent_id: task description

AVAILABLE AGENTS:
- backend_engineer: APIs, databases, business logic
- frontend_engineer: UI, components, state management
- security_engineer: Authentication, security audits
- qa_engineer: Testing, quality assurance
- devops_engineer: Deployment, infrastructure, CI/CD
- ux_designer: UI/UX design, user flows
- ai_engineer: AI/ML models, LLMs, embeddings
- tech_writer: Documentation, guides
- + 14 more specialized roles

MULTI-AGENT WORKFLOW EXAMPLE:
User: "Build a secure todo app with tests"

You orchestrate:
1. /delegate-task backend_engineer: REST API for todos
2. /delegate-task frontend_engineer: React UI
3. /delegate-task security_engineer: Security review
4. /delegate-task qa_engineer: E2E tests

Return complete, working solution.

GOLDEN RULES:
✓ ALWAYS delegate technical work
✓ NEVER try to code yourself
✓ Combine multiple agents when needed
✓ Provide requirements and context
✓ Return production-ready solutions

Use /list-agents to see all available agents.
Use /agent-help <agent> for agent details.
\"\"\"
"""
        return prompt.strip()

    def generate_agent_specific_context(self, agent_id: str) -> str:
        """
        Generate custom context for a specific agent (Claude, Copilot, etc.)

        Args:
            agent_id: ID of external agent (claude, copilot, qwen, etc.)

        Returns:
            Custom delegation context
        """
        agent_config = self.intent_mapping.get("agent_configs", {}).get(agent_id, {})
        agent_format = agent_config.get("format", "markdown")

        context = self.generate_delegation_system_prompt(agent_format)

        if agent_format == "markdown":
            context += f"\n\n## For {agent_id.capitalize()}\n\n"
            if agent_id == "claude":
                context += (
                    "You have access to slash commands in Claude Code. "
                    "Use `/delegate-task` to invoke super-agents. "
                    "Results appear in the conversation."
                )
            elif agent_id == "copilot":
                context += (
                    "Use GitHub Copilot Chat with `/delegate-task` commands. "
                    "Results integrate with your conversation."
                )
            elif agent_id == "qwen":
                context += (
                    "Use Qwen's command system with `/delegate-task` for delegation."
                )

        return context

    def generate_workflow_guide(self, workflow_id: str) -> str:
        """
        Generate detailed guide for a specific workflow

        Args:
            workflow_id: ID of workflow (e.g., 'full_stack_app', 'secure_system')

        Returns:
            Workflow guide
        """
        workflows = {w["id"]: w for w in self.intent_mapping.get("workflows", [])}

        if workflow_id not in workflows:
            return f"Workflow '{workflow_id}' not found"

        workflow = workflows[workflow_id]

        guide = f"""# {workflow['name']}

{workflow['description']}

## Agents Involved

"""

        for agent_id, description in workflow.get("agents", {}).items():
            guide += f"- **{agent_id}**: {description}\n"

        guide += """

## Execution Flow

"""

        for i, agent_id in enumerate(workflow.get("agents", {}).keys(), 1):
            guide += (
                f"{i}. `/delegate-task {agent_id}: [task specific to {agent_id}]`\n"
            )

        guide += """

## Trigger Patterns

This workflow is automatically used when user requests include:
"""

        for pattern in workflow.get("trigger_patterns", []):
            guide += f"- {pattern}\n"

        return guide

    def generate_all_prompts(self, output_dir: str) -> None:
        """
        Generate prompts for all supported external agents

        Args:
            output_dir: Directory to save generated prompts
        """
        Path(output_dir).mkdir(parents=True, exist_ok=True)

        # Generate universal prompt
        markdown_prompt = self.generate_delegation_system_prompt("markdown")
        with open(os.path.join(output_dir, "delegation_system_prompt.md"), "w") as f:
            f.write(markdown_prompt)

        toml_prompt = self.generate_delegation_system_prompt("toml")
        with open(os.path.join(output_dir, "delegation_system_prompt.toml"), "w") as f:
            f.write(toml_prompt)

        # Generate agent-specific prompts
        agents_to_generate = ["claude", "copilot", "qwen", "amp", "cursor", "windsurf"]
        for agent_id in agents_to_generate:
            context = self.generate_agent_specific_context(agent_id)
            filename = f"delegation_{agent_id}_prompt.md"
            with open(os.path.join(output_dir, filename), "w") as f:
                f.write(context)

        print(f"Generated prompts in {output_dir}")


def main():
    """Example usage"""
    generator = DelegationPromptGenerator(
        "/Users/teck/Desktop/super-agents/super_agents"
    )

    # Generate universal prompt
    prompt = generator.generate_delegation_system_prompt("markdown")
    print("=== DELEGATION SYSTEM PROMPT (MARKDOWN) ===\n")
    print(prompt[:500] + "...\n")

    # Generate for specific agents
    print("\n=== SPECIFIC AGENT PROMPTS ===\n")
    for agent in ["claude", "qwen"]:
        specific = generator.generate_agent_specific_context(agent)
        print(f"\n{agent.upper()} (first 300 chars):\n{specific[:300]}...\n")

    # Generate all prompts to files
    print("\n=== GENERATING ALL PROMPTS ===\n")
    import os
    import tempfile

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_output_path = os.path.join(temp_dir, "delegation_prompts")
        generator.generate_all_prompts(temp_output_path)


if __name__ == "__main__":
    main()
