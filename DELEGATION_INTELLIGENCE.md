# Automatic Delegation Intelligence System

## Overview

This document defines how external AI agents (Claude, Copilot, Qwen, Amp, etc.) should **automatically** recognize when to delegate work to specialized super-agents and route requests appropriately without requiring the user to explicitly invoke delegation.

The system transforms the super-agents from a manual tool into an **intelligent, automatic coordination system**.

---

## Core Principle

**When a user asks for something, the external agent should automatically determine which super-agent(s) can best handle it and delegate accordingly.**

This requires:
1. **Intent Recognition** - Parse user requests to identify the type of work
2. **Agent Selection** - Map intent to appropriate super-agent(s)
3. **Automatic Invocation** - Use `/delegate-task` without user asking
4. **Composition** - Handle multi-agent workflows automatically

---

## Intent-to-Agent Mapping

### Engineering Tasks

| User Request | Primary Agent | Supporting Agents | Intent Pattern |
|---|---|---|---|
| "Build an API for..." | backend_engineer | devops_engineer, security_engineer | api\|endpoint\|backend\|service\|database |
| "Design database schema..." | backend_engineer | devops_engineer | schema\|database\|postgresql\|table |
| "Create UI components..." | frontend_engineer | ux_designer | ui\|component\|button\|form\|react\|vue |
| "Build a login system..." | backend_engineer, security_engineer | frontend_engineer, qa_engineer | auth\|login\|session\|token\|jwt |
| "Deploy the app..." | devops_engineer | backend_engineer, frontend_engineer | deploy\|ci\/cd\|pipeline\|docker\|kubernetes |
| "Test the system..." | qa_engineer | backend_engineer, frontend_engineer | test\|qa\|validate\|integration\|coverage |
| "Secure the API..." | security_engineer | backend_engineer, devops_engineer | secure\|auth\|encrypt\|vulnerability\|audit |
| "Optimize performance..." | backend_engineer, devops_engineer | qa_engineer | performance\|optimize\|speed\|latency\|slow |

### Product & Design Tasks

| User Request | Primary Agent | Supporting Agents | Intent Pattern |
|---|---|---|---|
| "Design the UI..." | ux_designer | product_manager, frontend_engineer | design\|ui\|layout\|flow\|mockup |
| "Define requirements..." | product_manager | market_analyst, ux_designer | requirement\|spec\|definition\|scope |
| "Analyze the market..." | market_analyst | product_manager, research_agent | market\|trend\|research\|analysis\|competitor |
| "Build the spec..." | builder_engineer | product_manager | spec\|specification\|build\|generate |

### Quality & Security

| User Request | Primary Agent | Supporting Agents | Intent Pattern |
|---|---|---|---|
| "Review security..." | security_engineer | qa_engineer, devops_engineer | security\|vulnerability\|penetration\|audit\|compliance |
| "Run tests..." | qa_engineer | backend_engineer, frontend_engineer | test\|qa\|coverage\|integration\|e2e |
| "Ensure reliability..." | reliability_engineer | devops_engineer, qa_engineer | reliable\|uptime\|monitor\|alert\|health |

### Documentation & Operations

| User Request | Primary Agent | Supporting Agents | Intent Pattern |
|---|---|---|---|
| "Write documentation..." | tech_writer | backend_engineer, frontend_engineer | document\|guide\|readme\|tutorial\|explain |
| "Automate operations..." | ops_automator | devops_engineer | automate\|script\|cron\|scheduled\|task |
| "Organize knowledge..." | knowledge_architect | tech_writer | knowledge\|organize\|wiki\|faq\|learn |

### AI & Advanced

| User Request | Primary Agent | Supporting Agents | Intent Pattern |
|---|---|---|---|
| "Build AI features..." | ai_engineer | backend_engineer, product_manager | ai\|ml\|neural\|model\|training\|llm |
| "Research solutions..." | research_agent | ai_engineer, backend_engineer | research\|explore\|investigate\|poc\|spike |

### Executive & Strategic

| User Request | Primary Agent | Supporting Agents | Intent Pattern |
|---|---|---|---|
| "Plan the project..." | ceo, product_manager | cto, coo | plan\|strategy\|roadmap\|goal\|vision |
| "Allocate resources..." | coo | cto, ceo | allocate\|resource\|team\|manage\|organize |
| "Technical strategy..." | cto | backend_engineer, ai_engineer | technical\|architecture\|standard\|framework |

---

## Automatic Delegation Patterns

### Pattern 1: Single-Agent Tasks

**When user request maps to ONE primary agent:**

```
User: "Build an API endpoint for user registration"
        ↓
External Agent (Claude/Copilot) detects:
  - Intent: API development
  - Specialist: backend_engineer
        ↓
Automatically invokes:
  /delegate-task backend_engineer: Design and implement a user registration API endpoint with proper validation, error handling, and security measures
        ↓
Result: Returns to user with implementation
```

### Pattern 2: Multi-Agent Sequential Workflow

**When task requires PRIMARY agent + SUPPORTING agents in sequence:**

```
User: "Build a secure login system"
        ↓
External Agent detects:
  - Primary intent: Backend service
  - But also requires: security + frontend
        ↓
Orchestrates sequence:
  1. /delegate-task backend_engineer: Design session/token management backend
  2. /delegate-task security_engineer: Implement authentication and secret management
  3. /delegate-task frontend_engineer: Create login form UI
  4. /delegate-task qa_engineer: Write integration tests
        ↓
Returns integrated result with all components
```

### Pattern 3: Parallel Multi-Agent Tasks

**When agents can work independently:**

```
User: "Build the entire app: API, UI, tests, and docs"
        ↓
External Agent detects independent tasks:
  - Backend API (backend_engineer)
  - UI Components (frontend_engineer)
  - Test Suite (qa_engineer)
  - Documentation (tech_writer)
        ↓
Invokes in parallel:
  /delegate-task backend_engineer: Build REST API with authentication
  /delegate-task frontend_engineer: Build React components
  /delegate-task qa_engineer: Create comprehensive test suite
  /delegate-task tech_writer: Write API documentation
        ↓
Aggregates all results
```

### Pattern 4: Expert Review/Refinement

**When implementation needs validation:**

```
User: "I need authentication - make sure it's secure"
        ↓
External Agent detects:
  - Primary: backend_engineer (build auth)
  - Review: security_engineer (validate)
        ↓
Orchestrates:
  1. /delegate-task backend_engineer: Implement JWT authentication
  2. /delegate-task security_engineer: Review implementation for vulnerabilities
  3. Incorporates security feedback into final result
```

---

## Decision Tree for Automatic Delegation

```
User Request
    │
    ├─ Is this a technical task?
    │  ├─ YES: Continue
    │  └─ NO: Handle normally (no delegation)
    │
    ├─ Extract key terms/intent from request
    │  (API, database, UI, security, deploy, test, etc.)
    │
    ├─ Map to super-agent(s) using Intent-to-Agent table
    │  ├─ Found PRIMARY agent: Use Pattern 1 or 2
    │  ├─ Found multiple agents: Use Pattern 2, 3, or 4
    │  └─ No match: Handle normally or ask for clarification
    │
    ├─ Can agents work independently?
    │  ├─ YES: Use Pattern 3 (parallel)
    │  └─ NO: Use Pattern 2 (sequential)
    │
    ├─ Build delegation request(s)
    │  ├─ Include context from user message
    │  ├─ Add task-specific requirements
    │  └─ Format for super-agent consumption
    │
    └─ Invoke /delegate-task and return results
```

---

## Context Injection for External Agents

Every external agent should receive this system prompt injection:

```markdown
## Super-Agents Delegation System

You have access to specialized super-agents that handle different aspects 
of software development. When a user asks you to build something technical, 
you should AUTOMATICALLY recognize the type of work and delegate to the 
appropriate expert(s).

### Available Super-Agents:
- **backend_engineer**: API, database, business logic
- **frontend_engineer**: UI, components, state management
- **security_engineer**: Authentication, encryption, auditing
- **qa_engineer**: Testing, quality assurance, validation
- **devops_engineer**: Deployment, CI/CD, infrastructure
- **ux_designer**: UI/UX design, flows, accessibility
- **ai_engineer**: ML models, AI features, LLMs
- **tech_writer**: Documentation, guides, tutorials
- And 14+ more specialized roles...

### Delegation Examples:
1. User: "Build a REST API"
   → You: /delegate-task backend_engineer: Build REST API with [requirements]

2. User: "Create a login page"
   → You: /delegate-task frontend_engineer: Design login form [requirements]
          /delegate-task security_engineer: Implement authentication [security requirements]

3. User: "Build and test everything"
   → You: Invoke multiple agents in parallel

### Golden Rules:
✓ ALWAYS delegate technical work - don't try to do it yourself
✓ ALWAYS include requirements and context in delegation
✓ ALWAYS combine results from multiple agents when needed
✓ NEVER ask user to manually delegate - do it automatically
✓ Think like a dev company - orchestrate specialists together
```

---

## Implementation: Prompt Templates for Each Agent

### For Claude Code/IDE Agents

Add to `.claude/commands/super-agents-init.md`:

```markdown
## Your Super-Agent Team

You now have access to 22 specialized AI agents that form a complete 
software development company. Your role is to orchestrate them.

### Key Principles:
1. **Automatic Recognition**: When a user asks for a technical task, 
   automatically determine which agent(s) should handle it
2. **Delegation**: Use `/delegate-task agent_id: task description` 
   to invoke specialized agents
3. **Orchestration**: Combine multiple agents for complex workflows

### Quick Recognition Guide:
- "Build API" → backend_engineer
- "Design UI" → frontend_engineer  
- "Make it secure" → security_engineer
- "Test this" → qa_engineer
- "Deploy it" → devops_engineer

Use /agent-help <agent> for full details on any agent.
```

### For Qwen Code

Add to `.qwen/commands/super-agents-init.toml`:

```toml
description = "Initialize super-agents delegation system"

prompt = """
SUPER-AGENTS COORDINATION MODE ENABLED

You are now the orchestrator of a 22-agent software development company.
Your job is to automatically recognize what users are asking for and 
delegate to the right specialists.

## Automatic Recognition Rules:

When user says...          Delegate to...
"Build API"                backend_engineer
"Create UI"                frontend_engineer
"Make it secure"           security_engineer
"Test the system"          qa_engineer
"Deploy the app"           devops_engineer
"Design the layout"        ux_designer
"Add AI features"          ai_engineer
"Write docs"               tech_writer

## Example Workflow:
User: "Build a user authentication system"

You recognize this requires:
1. Backend service (tokens, sessions) → backend_engineer
2. Security measures (encryption) → security_engineer
3. Frontend UI (login form) → frontend_engineer
4. Test coverage → qa_engineer

So you invoke:
/delegate-task backend_engineer: Implement JWT authentication system
/delegate-task security_engineer: Review and harden authentication
/delegate-task frontend_engineer: Create login/signup forms
/delegate-task qa_engineer: Write integration tests

Then combine results into complete solution.
"""
```

---

## Advanced Routing: Intent Scoring

For more sophisticated routing, external agents should implement scoring:

```
Task: "Optimize API performance"

Score matching agents:
- backend_engineer: 0.95 (core API expertise)
- devops_engineer: 0.85 (infrastructure optimization)
- qa_engineer: 0.60 (performance testing)
- ai_engineer: 0.20 (not relevant)

Primary agent: backend_engineer (highest score)
Supporting: devops_engineer, qa_engineer
```

---

## Context Management: What to Include in Delegation

When delegating, always provide:

```
/delegate-task <agent>: <task_description>
  
Requirements to include:
1. WHAT: Specific deliverable or feature
2. WHY: Business context and importance
3. HOW: Technical approach or constraints
4. ACCEPTANCE: Success criteria or examples
5. CONTEXT: Related code, specs, or documentation
```

Example:
```
/delegate-task backend_engineer: Design a PostgreSQL schema for:
  WHAT: User profile management system
  WHY: Support user accounts across platform
  HOW: Use normalized schema, ensure GDPR compliance
  ACCEPTANCE: Support 1M users, <100ms queries
  CONTEXT: User can have multiple profiles, profiles have permissions
```

---

## Feedback Loop: Improving Delegation

External agents should:

1. **Ask**: After delegation, check if result meets user needs
2. **Refine**: If not, provide feedback to super-agent
3. **Iterate**: Use additional agents to polish results
4. **Document**: Remember what works for future similar tasks

Example:
```
Initial delegation result → "Good, but API endpoints need rate limiting"
      ↓
Refined delegation: /delegate-task backend_engineer: Add rate limiting to API
      ↓
Result → User approval
```

---

## Success Metrics

An effective automatic delegation system should result in:

✓ **Zero manual delegation**: Users never type `/delegate-task` themselves
✓ **Intelligent routing**: Right agent for each task
✓ **Efficient workflows**: Multi-agent tasks orchestrated smoothly  
✓ **Quality output**: Expert-level work from specialists
✓ **Fast turnaround**: Parallel execution when possible
✓ **Complete solutions**: All aspects addressed (backend, frontend, security, tests, docs)

---

## Examples: Real-World Scenarios

### Scenario 1: "Build a todo app"

System recognizes: Full-stack application

Automatic routing:
```
backend_engineer: REST API for todos (CRUD operations)
frontend_engineer: React UI with state management
security_engineer: Authentication and data protection
qa_engineer: E2E tests
tech_writer: API documentation
devops_engineer: Deployment pipeline
```

### Scenario 2: "Make the app faster"

System recognizes: Performance optimization

Automatic routing:
```
backend_engineer: Profile API, optimize queries
devops_engineer: Infrastructure optimization, caching
frontend_engineer: UI performance, code splitting
qa_engineer: Performance benchmarking
```

### Scenario 3: "Fix security vulnerabilities"

System recognizes: Security assessment + remediation

Automatic routing:
```
security_engineer: Vulnerability audit, fixes
backend_engineer: Implement security patches
devops_engineer: Update dependencies, patch systems
qa_engineer: Security testing
```

---

## Configuration for Each External Agent

Different agents may need slightly different prompts. Store in:

```
company/
├── delegation_intelligence/
│   ├── claude_delegation_prompt.md
│   ├── copilot_delegation_prompt.md
│   ├── qwen_delegation_prompt.md
│   ├── amp_delegation_prompt.md
│   ├── cursor_delegation_prompt.md
│   ├── windsurf_delegation_prompt.md
│   └── intent_to_agent_mapping.yaml ← Universal mapping
```

---

## Next Steps

1. **Update command files** - Add delegation intelligence to super-agents-init in each agent format
2. **Create agent-specific prompts** - Customize for Claude, Copilot, Qwen, etc.
3. **Build intent recognizer** - Optional: Add programmatic intent detection
4. **Document workflows** - Create examples for common tasks
5. **Test automatic delegation** - Verify agents delegate appropriately

This transforms super-agents from a *manual tool* into an *automatic dev company*.
