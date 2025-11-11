# Super-Agents Context for claude

Last updated: 2025-11-11 11:17:38

This file provides context for working with AICODE Labs super-agents.

## Complete Super-Agent Specifications

For complete super-agent specifications, see:
- super-agents-context.yaml (in the same directory)
- The agent specifications in /Users/teck/Desktop/super-agents/company/agents/

## How to Use Super-Agents

The super-agents system allows you to delegate specialized tasks to autonomous agents.
Each agent has specific capabilities and responsibilities within the AICODE Labs organization.

### Agent Categories:

- **Executive Division**: CEO, CTO, COO for strategic decisions
- **Product Division**: Product Manager, UX Designer, Market Analyst for requirements
- **Engineering Division**: Backend, Frontend, AI, DevOps Engineers for implementation
- **Quality Division**: QA and Reliability Engineers for validation
- **Security Division**: Security Engineer for protection measures
- **Knowledge Division**: Tech Writer and Knowledge Architect for documentation
- **Governance Division**: Meta Architect for system evolution
- **Expansion Division**: Finance Agent, Research Agent, etc. for growth

### Task Delegation Pattern

Use the delegation pattern to coordinate with super-agents:

```
@agent_id: Your task description here
```

### Examples:

```
@backend_engineer: Design a REST API for product catalog with Postgres backend
@ux_designer: Create mobile-responsive UI components for dashboard
@qa_engineer: Write integration tests for payment flow
@security_engineer: Implement OAuth2 authentication with JWT tokens
@devops_engineer: Set up CI/CD pipeline with Docker and Kubernetes
@ai_engineer: Create recommendation engine model using LangChain
```

### Best Practices

1. Be specific about requirements and constraints
2. Reference existing specifications when relevant
3. Include success criteria and acceptance tests when applicable
4. Consider dependencies on other agents' work
5. Plan complex workflows across multiple agents

