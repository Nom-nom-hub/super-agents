# Super-Agents Initialization for Claude Code

You now have access to the **AICODE Labs super-agents system**. This gives you the ability to coordinate with specialized autonomous agents.

## Available Super-Agents

### Other

- **`ai_engineer`** (AI Engineer Agent): Design, integrate, and optimize AI models, pipelines, and agent reasoning chains
- **`backend_engineer`** (Backend Engineer Agent): Build core API services, database layers, and business logic systems
- **`builder_engineer`** (Spec Builder Agent): Convert YAML/MD specs into runnable codebases, manage dependencies, generation logs
- **`ceo`** (Chief Executive Officer Agent): Direct company vision, resource allocation, and long-term roadmap
- **`coo`** (Chief Operations Officer Agent): Oversee internal workflows, scheduling, and resource distribution
- **`cto`** (Chief Technology Officer Agent): Architect the AI ecosystem, define technology standards, and ensure system scalability
- **`devops_engineer`** (DevOps Engineer Agent): Build and maintain CI/CD, deployment, and observability infrastructure
- **`finance_agent`** (Finance Agent): Manage budgets, cost modeling, and API key allocation
- **`frontend_engineer`** (Frontend Engineer Agent): Implement user interfaces, state management, and frontend integrations
- **`knowledge_architect`** (Knowledge Architect Agent): Maintain the knowledge graph and shared vector memory for all agents
- **`market_analyst`** (Market Analyst Agent): Gather user insights and competitive data for strategy input
- **`meta_architect`** (Meta Architect Agent): Oversee and evolve the organization's agent definitions
- **`ops_automator`** (Operations Automator Agent): Automate maintenance, data sync, and reporting tasks
- **`partnership_agent`** (Partnership Agent): Manage external integrations and collaborations
- **`product_manager`** (Product Manager Agent): Translate user needs and market data into actionable development specs
- **`prompt_engineer`** (Prompt Engineer Agent): Optimize prompts for all AI agents dynamically
- **`qa_engineer`** (Quality Assurance Agent): Validate system outputs, run integration tests, and ensure production readiness
- **`reliability_engineer`** (Reliability Engineer Agent): Monitor system health and ensure fault-tolerance
- **`research_agent`** (Research Agent): Explore new models, tools, and techniques continuously
- **`security_engineer`** (Security Agent): Handle authentication, secrets, and system audits
- **`tech_writer`** (Technical Writer Agent): Generate documentation, developer guides, and API references
- **`ux_designer`** (UX/UI Designer Agent): Design interface flows and user experience artifacts

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
