# Agent Command Interface for AICODE Labs

## Overview

This document describes how to interact with the AICODE Labs AI agents using `/` commands. The command interface allows you to delegate tasks to specific agents based on their specializations, enabling efficient collaboration in the AI-native software development company.

## Command Syntax

Basic command format:

```
@task [agent-type] [detailed-task-description]
```

## Agent Command Mappings

### Executive Division

- `/ceo` → Use for strategic decisions, resource allocation, production sign-offs

  ```
  @task ceo Define quarterly strategic objectives and approve production release
  ```

- `/cto` → Use for technical architecture, system design, and technology standards

  ```
  @task cto Architect AI systems and define technical standards for scalability
  ```

- `/coo` → Use for operational workflows, resource distribution, scheduling

  ```
  @task coo Coordinate release process and optimize operational workflows
  ```

### Product Division

- `/product_manager` → Use for product specifications, user needs translation, market analysis

  ```
  @task product_manager Create product specifications from market analysis
  ```

- `/ux_designer` → Use for interface design, user experience artifacts, design systems

  ```
  @task ux_designer Design user interface flows and create design system
  ```

- `/market_analyst` → Use for market research, user insights, competitive analysis

  ```
  @task market_analyst Gather user insights and analyze market trends
  ```

### Engineering Division

- `/backend_engineer` → Use for APIs, databases, business logic, server architecture

  ```
  @task backend_engineer Design and implement REST API endpoints for user authentication
  ```

- `/frontend_engineer` → Use for UI components, state management, frontend integrations

  ```
  @task frontend_engineer Create responsive navigation component with accessibility features
  ```

- `/ai_engineer` → Use for AI models, ML pipelines, reasoning chains, NLP processing

  ```
  @task ai_engineer Design and implement AI model for sentiment analysis
  ```

- `/devops_engineer` → Use for CI/CD, deployment, observability, infrastructure

  ```
  @task devops_engineer Set up CI/CD pipeline with automated testing and deployment
  ```

- `/builder_engineer` → Use for spec-to-code conversion, dependency management, code generation

  ```
  @task builder_engineer Convert YAML specifications into runnable codebase
  ```

### Quality Division

- `/qa_engineer` → Use for testing, quality assurance, integration tests, performance validation

  ```
  @task qa_engineer Write comprehensive test coverage for the payment module
  ```

- `/reliability_engineer` → Use for system monitoring, fault tolerance, uptime assurance

  ```
  @task reliability_engineer Implement monitoring and alerting for system health
  ```

### Security Division

- `/security_engineer` → Use for authentication, secrets management, security audits
  ```
  @task security_engineer Implement authentication system and manage secrets
  ```

### Knowledge Division

- `/tech_writer` → Use for documentation, API references, developer guides

  ```
  @task tech_writer Create API documentation and user guides
  ```

- `/knowledge_architect` → Use for knowledge graphs, vector memory, information retrieval

  ```
  @task knowledge_architect Maintain knowledge graph and shared vector memory
  ```

### Governance Division

- `/meta_architect` → Use for agent definitions, schema validation, system evolution
  ```
  @task meta_architect Update agent specifications and validate compliance
  ```

### Expansion Division

- `/finance_agent` → Use for budget management, cost modeling, resource allocation

  ```
  @task finance_agent Model API consumption costs and allocate budgets
  ```

- `/partnership_agent` → Use for integrations, collaborations, vendor management

  ```
  @task partnership_agent Integrate with external API and manage partnership
  ```

- `/prompt_engineer` → Use for prompt optimization, A/B testing, performance tuning

  ```
  @task prompt_engineer Optimize prompts for better AI agent performance
  ```

- `/research_agent` → Use for model research, technology scanning, innovation tracking

  ```
  @task research_agent Research new AI models and evaluate their applicability
  ```

- `/ops_automator` → Use for process automation, data sync, report generation

  ```
  @task ops_automator Automate daily maintenance and reporting tasks
  ```

## Best Practices for Agent Commands

### 1. Provide Sufficient Context

Always include relevant context for the agent to perform the task effectively:

```
@task backend_engineer Design and implement REST API endpoints for user authentication following our OAuth 2.0 security standards and PostgreSQL database schema defined in database_schema.sql
```

### 2. Be Specific About Requirements

Include specific requirements, constraints, or standards:

```
@task frontend_engineer Create responsive navigation component with accessibility features, ensuring WCAG 2.1 AA compliance and mobile-first design approach
```

### 3. Reference Existing Artifacts

When applicable, reference existing files, documents, or specifications:

```
@task product_manager Create product specifications based on market_analysis.md and align with design_system.yaml
```

### 4. Chain Related Tasks

For complex workflows, chain related tasks across multiple agents:

```
@task market_analyst Gather user insights and competitive data
@task product_manager Create product specifications from market analysis
@task ux_designer Design interface flows based on product specifications
@task frontend_engineer Implement UI components based on design flows
```

### 5. Leverage Agent Collaboration

Some tasks require multiple agents to work together:

```
@task backend_engineer Build API services following product specifications
@task frontend_engineer Implement UI components that consume the API
@task devops_engineer Create deployment pipeline for both components
@task qa_engineer Validate integration between frontend and backend
```

## Example Workflows

### Full Product Development Cycle

```
@task market_analyst Conduct market research for new product feature
@task product_manager Create product specifications based on market insights
@task ux_designer Design user interface flows for the new feature
@task ai_engineer Implement AI capabilities required for the feature
@task backend_engineer Build core API services for the feature
@task frontend_engineer Implement frontend UI components
@task devops_engineer Set up CI/CD pipeline for deployment
@task qa_engineer Validate functionality and performance
@task security_engineer Review implementation for security compliance
@task tech_writer Create documentation for the new feature
@task coo Coordinate release process
@task ceo Approve production deployment
```

### Technical Architecture Design

```
@task cto Define technical architecture for microservices approach
@task security_engineer Design security framework for the architecture
@task database_engineer Design database schemas aligned with architecture
@task devops_engineer Create infrastructure as code for the architecture
@task ai_engineer Design AI service integration points
@task tech_lead Review architectural decisions and provide feedback
```

## Command Validation

When using agent commands, ensure that:

1. The agent type matches the task requirements
1. Sufficient context is provided for successful completion
1. Dependencies between tasks are properly ordered
1. Resources and artifacts referenced actually exist
1. The task aligns with the agent's capabilities and mission

## Troubleshooting

If an agent command doesn't produce expected results:

1. Verify the agent type is correct and matches the specialization
1. Check that sufficient context and resources are provided
1. Confirm that the task is within the agent's domain of expertise
1. Review the agent's specific capabilities and limitations
1. Consider breaking complex tasks into smaller, more focused commands
