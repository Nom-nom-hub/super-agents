# Autonomous Learning System - Quick Reference

## One-Liner

> Every agent execution automatically captures telemetry, analyzes patterns, updates specs, and broadcasts changes.

## Key Message

```
[Autonomous Learning] Spec regeneration completed for {agent_id}, now at v{version}
```

---

## Quick Start

### For Orchestrator (Already Integrated)

```python
from agent_orchestrator import AgentOrchestrator

orchestrator = AgentOrchestrator("./company")
orchestrator.load_agent_specs()
orchestrator.instantiate_agents()
orchestrator.run_demo_workflow()

# Each task automatically triggers:
# [Autonomous Learning] Spec regeneration completed for backend_engineer, now at v2
```

### For External Agents

```python
from learning_integration import LearningIntegration

learning = LearningIntegration("./company")

# Pre-execution
learning.pre_execute(agent_id, task_description)

# Track during execution
learning.track_tool("FastAPI", "Web framework")
learning.track_decision("Use async/await", "Better performance")
learning.track_blocker("Pool sizing", "Researched docs")
learning.track_output("api.py", "Main API")
learning.track_metrics(test_coverage=92, code_quality_score=8.7)

# Post-execution (triggers learning)
result = learning.post_execute(agent_id)
```

---

## Core Components

| Component | File | Purpose |
|-----------|------|---------|
| **ExecutionTracker** | `execution_tracker.py` | Captures telemetry |
| **ReflectionAgent** | `reflection_agent.py` | Analyzes patterns |
| **AutonomousSpecManager** | `autonomous_spec_manager.py` | Versions & updates specs |
| **AgentSupport** | `agent_support.py` | Integration layer |
| **LearningIntegration** | `learning_integration.py` | External integration |
| **Agent Orchestrator** | `agent_orchestrator.py` | Integrated runner |

---

## Data Captured

During each execution, the system tracks:

```
Tools Used      → Promoted to capabilities if frequent
Decisions Made  → Analyzed for patterns
Blockers        → Flagged for attention
Outputs         → Counted for productivity
Metrics         → Code quality, test coverage, latency, LOC
Duration        → Performance baseline
Status          → Success/failure classification
```

---

## What Happens After Execution

1. **ExecutionTracker** saves log to `.execution_logs/`
2. **ReflectionAgent** analyzes patterns and learnings
3. **AutonomousSpecManager** updates spec to next version
4. **Previous spec** archived to `.history/`
5. **Intent mappings** updated if specialization detected
6. **Delegation prompts** refreshed
7. **Learning reports** generated
8. **Console logs** "[Autonomous Learning] Spec regeneration..."

---

## Spec Evolution Example

### Execution 1: Basic API

```
Execution: "Design REST API"
Tools: FastAPI, PostgreSQL
Decisions: Use async/await, implement validation
Metrics: 90% coverage, 8.5 quality score

Result: v1 → v2
  +tools: asyncio
  +capabilities: Async API Design
```

### Execution 2: High-Traffic API

```
Execution: "Build high-traffic API"
Tools: FastAPI, PostgreSQL, Redis, asyncio
Decisions: Connection pooling, implement caching
Metrics: 92% coverage, 8.7 quality score

Result: v2 → v3
  +tools: Redis, connection_pool_manager
  +capabilities: Connection Pooling, Caching
  +specialization: "high-traffic API"
```

### Execution 3: Secure API

```
Execution: "Build secure API with audit logging"
Tools: FastAPI, PostgreSQL, Redis, asyncio, Pydantic
Decisions: Input validation, audit logging, compliance
Metrics: 95% coverage, 9.1 quality score

Result: v3 → v4
  +tools: Pydantic
  +capabilities: Input Validation, Audit Logging
  +specialization_confidence: higher
```

---

## File Structure

```
company/agents/
├── backend_engineer_agent.yaml          (current v3)
│
├── .execution_logs/                     (telemetry)
│   ├── exec_backend_engineer_1762884762067.json
│   ├── exec_backend_engineer_1762884762200.json
│   └── ...
│
├── .history/                            (versions)
│   ├── backend_engineer_agent_v1.yaml
│   ├── backend_engineer_agent_v2.yaml
│   └── backend_engineer_agent_v3.yaml
│
└── .learning_reports/                   (analysis)
    ├── backend_engineer_20251111_130000.md
    ├── backend_engineer_20251111_131000.md
    └── backend_engineer_20251111_132000.md
```

---

## API Cheat Sheet

### LearningIntegration Methods

```python
learning = LearningIntegration("./company")

# Tracking
learning.pre_execute(agent_id, task)
learning.track_tool(name, context)
learning.track_decision(decision, rationale)
learning.track_blocker(blocker, resolution)
learning.track_output(path, description)
learning.track_metrics(test_coverage=X, code_quality_score=Y, ...)

# Learning
learning.post_execute(agent_id, status="completed")

# Analysis
learning.get_agent_stats(agent_id)
learning.get_agent_evolution(agent_id)
learning.get_spec_history(agent_id)

# Management
learning.rollback_spec(agent_id, target_version=3)
```

---

## Governance

### Auto-Flagged for Review

- Major version increment (≥3 versions)
- 5+ new capabilities added
- 8+ new tools added

### Spec Rollback

```python
learning.rollback_spec("agent_id", target_version=2)
# Rolls back to v2, archives current version
```

---

## Integration Points

### In Agent Orchestrator

```python
# Automatic integration:
# 1. Initialize agent_support in AgentOrchestrator.__init__()
# 2. Pass to all agents in instantiate_agents()
# 3. Hook into Agent.execute_task():
#    - Pre-execution: track_execution_start()
#    - During: track_execution_tool/decision/metrics()
#    - Post-execution: end_execution_and_learn()
```

### In External Agents

```python
from learning_integration import LearningIntegration

# Just use LearningIntegration class
# No changes to existing agent code needed
```

---

## Verification Commands

### Check spec version
```bash
cd company/agents
grep "version:" backend_engineer_agent.yaml
```

### View execution logs
```bash
ls -la company/agents/.execution_logs/
```

### View version history
```bash
ls -la company/agents/.history/
```

### View learning reports
```bash
ls -la company/agents/.learning_reports/
cat company/agents/.learning_reports/backend_engineer_*.md
```

### Check intent mappings
```bash
grep -A5 "backend_engineer" company/intent_mapping.yaml
```

---

## Common Metrics

| Metric | Range | Typical |
|--------|-------|---------|
| test_coverage | 0-100 | 85-95 |
| code_quality_score | 0-10 | 8-9 |
| performance_latency_ms | 0+ | 30-150 |
| lines_of_code | 0+ | 500-2000 |

---

## Console Output Pattern

```
# Pre-execution
[Learning] Started tracking execution: exec_backend_engineer_1762884762067

# During execution
[backend_engineer] Using capability: Async Request Handling
[backend_engineer] Using capability: Connection Pooling

# Post-execution
[Autonomous Learning] Spec regeneration completed for backend_engineer, now at v3
```

---

## Troubleshooting

### Learning not triggered
- ✓ Check `agent_support` is initialized
- ✓ Verify `post_execute()` is called
- ✓ Check `status="completed"` (not "failed")

### Execution logs missing
- ✓ Check permissions on `company/agents/.execution_logs/`
- ✓ Verify ExecutionTracker saving properly

### Spec not updated
- ✓ Check learning reports in `.learning_reports/`
- ✓ Verify schema validation passed
- ✓ Check governance thresholds not exceeded

### Want to rollback
```python
learning.rollback_spec("agent_id", target_version=2)
```

---

## Next Integration Points

- [ ] Claude integration
- [ ] Copilot integration  
- [ ] Approval workflow for governance reviews
- [ ] Metrics dashboard
- [ ] Learning velocity metrics
- [ ] Notification system for specialization discovery

---

## Key Files

- **Integration:** `company/learning_integration.py`
- **Guide:** `company/LEARNING_INTEGRATION_GUIDE.md`
- **Report:** `INTEGRATION_COMPLETION_REPORT.md`
- **This file:** `AUTONOMOUS_LEARNING_QUICKREF.md`

---

**Status:** ✅ Production Ready
