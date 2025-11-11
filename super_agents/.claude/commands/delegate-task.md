# Delegate Task to Super-Agent

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
1. **Provide Context**: Include relevant constraints and examples
1. **Reference Specs**: Link to existing specifications when relevant
1. **Sequential Tasks**: Use multiple delegations for complex work
1. **Validation**: Ask `qa_engineer` to review critical work
