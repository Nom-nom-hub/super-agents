# Autonomous Learning System Integration Guide

## Overview

The autonomous spec regeneration system has been fully integrated into the runtime. Every agent execution now automatically:

1. **Captures execution telemetry** via ExecutionTracker
2. **Analyzes patterns** via ReflectionAgent
3. **Updates agent specs** via AutonomousSpecManager
4. **Broadcasts changes** to delegation system

This guide explains how to integrate the learning system into your agent runners.

---

## Quick Start

### For Agent Orchestrator (Built-in)

The agent orchestrator is already integrated. Simply run it:

```python
from agent_orchestrator import AgentOrchestrator

orchestrator = AgentOrchestrator("./company")
orchestrator.load_agent_specs()
orchestrator.instantiate_agents()
orchestrator.run_demo_workflow()

# After each task, agents automatically trigger learning:
# [Autonomous Learning] Spec regeneration completed for backend_engineer, now at v2
```

The orchestrator:
- Initializes `AgentSupport` with learning components
- Passes it to all Agent instances
- Automatically calls `track_execution_start()` at task start
- Automatically calls `end_execution_and_learn()` at task end

### For External Agent Runners

Use the `LearningIntegration` class:

```python
from learning_integration import LearningIntegration

learning = LearningIntegration("./company")

# Pre-execution
exec_id = learning.pre_execute("backend_engineer", "Design REST API")

# During execution, track everything
learning.track_tool("FastAPI", "API framework")
learning.track_tool("PostgreSQL", "Database")
learning.track_decision("Use async/await", "Better performance")
learning.track_blocker("Connection pool sizing", "Researched best practices")
learning.track_output("api.py", "Main API implementation")

# Track metrics
learning.track_metrics(
    test_coverage=92,
    code_quality_score=8.7,
    lines_of_code=750,
    performance_latency_ms=35
)

# Post-execution (automatically triggers learning cycle)
result = learning.post_execute("backend_engineer", status="completed")

if result["success"]:
    print(f"✓ Spec updated to v{result['spec_version']}")
    if result["learnings"]["specialization"]:
        print(f"  Specialization: {result['learnings']['specialization']}")
```

---

## Integration Points

### 1. Agent Orchestrator Integration

The `agent_orchestrator.py` has been enhanced:

```python
class Agent:
    def __init__(self, spec: AgentSpec, agent_support: Optional[AgentSupport] = None):
        self.agent_support = agent_support
    
    def execute_task(self, task_description: str, context: Dict[str, Any] = None):
        # PRE-EXECUTION HOOK
        if self.agent_support:
            self.agent_support.track_execution_start(self.id, task_description)
        
        # ... execute task ...
        
        # Track tools, decisions, metrics
        self.agent_support.track_execution_tool(tool_name, context)
        self.agent_support.track_execution_decision(decision, rationale)
        self.agent_support.track_execution_metrics(...)
        
        # POST-EXECUTION HOOK: Automatic learning
        if self.agent_support:
            self.agent_support.end_execution_and_learn(self.id, status="completed")
```

### 2. AgentSupport Integration

The `agent_support.py` provides the complete learning API:

```python
support = AgentSupport("./company")

# Pre-execution
exec_id = support.track_execution_start(agent_id, task)

# During execution
support.track_execution_tool(tool, context)
support.track_execution_decision(decision, rationale)
support.track_execution_blocker(blocker, resolution)
support.track_execution_output(path, description)
support.track_execution_metrics(**metrics)

# Post-execution with learning
result = support.end_execution_and_learn(agent_id, status="completed", result={...})
```

### 3. Standalone LearningIntegration

For external systems:

```python
from learning_integration import LearningIntegration

learning = LearningIntegration(company_dir)

# Simple wrapper for task execution
result, learning_result = execute_with_learning(
    company_dir,
    "backend_engineer",
    "Design API",
    my_task_function,
    param1=value1
)
```

---

## Component Architecture

```
┌─────────────────────────────────┐
│   Agent Execution               │
│   (Orchestrator / External)     │
└─────────────┬───────────────────┘
              │
              ├─ track_execution_start()
              ├─ track_execution_tool()
              ├─ track_execution_decision()
              ├─ track_execution_blocker()
              ├─ track_execution_output()
              ├─ track_execution_metrics()
              │
              └─ end_execution_and_learn()
                      │
                      ├─ ExecutionTracker
                      │   └─ Save execution log
                      │
                      ├─ ReflectionAgent
                      │   ├─ Analyze patterns
                      │   ├─ Extract capabilities
                      │   ├─ Detect specialization
                      │   └─ Validate changes
                      │
                      ├─ AutonomousSpecManager
                      │   ├─ Load current spec
                      │   ├─ Generate updated spec
                      │   ├─ Version & archive
                      │   └─ Update intent_mapping.yaml
                      │
                      └─ DelegationPromptGenerator
                          └─ Refresh delegation prompts
```

---

## Data Flow: Complete Example

### Before Integration

```
Task → Agent.execute_task() → [No tracking] → [Spec never updates]
```

### After Integration

```
1. PRE-EXECUTION
   └─ learning.pre_execute("backend_engineer", "Design REST API")
      └─ ExecutionTracker.start_execution()
         └─ Execution ID: exec_backend_engineer_1705329000000

2. DURING EXECUTION
   ├─ learning.track_tool("FastAPI", "API framework")
   ├─ learning.track_tool("PostgreSQL", "Database")
   ├─ learning.track_decision("Use async/await", "Better performance")
   ├─ learning.track_decision("Implement connection pooling", "Scalability")
   ├─ learning.track_blocker("Connection pool sizing", "Researched best practices")
   ├─ learning.track_output("api.py", "Main API implementation")
   └─ learning.track_metrics(test_coverage=92, code_quality_score=8.7, ...)

3. POST-EXECUTION & LEARNING
   └─ learning.post_execute("backend_engineer", status="completed")
      │
      ├─ ExecutionTracker
      │  └─ End execution & save log
      │     └─ company/agents/.execution_logs/exec_backend_engineer_*.json
      │
      ├─ ReflectionAgent
      │  ├─ Analyze execution patterns
      │  ├─ Discover: [FastAPI, PostgreSQL, asyncio]
      │  ├─ Extract capabilities: [Async Request Handling, Connection Pooling]
      │  └─ Learnings: {...}
      │
      ├─ AutonomousSpecManager
      │  ├─ Load current spec (v1)
      │  ├─ Generate updated spec (v2)
      │  │  ├─ +2 tools: asyncio, connection_pool_manager
      │  │  ├─ +2 capabilities: Async Handling, Connection Pooling
      │  │  └─ performance_baseline: {...}
      │  ├─ Validate schema
      │  ├─ Archive v1 → .history/backend_engineer_agent_v1.yaml
      │  ├─ Save v2 → backend_engineer_agent.yaml
      │  └─ Update intent_mapping.yaml
      │
      ├─ DelegationPromptGenerator
      │  └─ Refresh delegation prompts with new capabilities
      │
      └─ Console Output
         └─ "[Autonomous Learning] Spec regeneration completed for backend_engineer, now at v2"

4. NEXT EXECUTION (Agent is now smarter!)
   └─ Agent "knows" about async/await patterns from v2 spec
```

---

## API Reference

### LearningIntegration Class

Main integration point for learning system.

#### Methods

##### `is_available() → bool`
Check if learning system is initialized.

##### `pre_execute(agent_id: str, task_description: str) → Optional[str]`
Start tracking execution. Call before task execution.

**Returns:** Execution ID or None

**Example:**
```python
exec_id = learning.pre_execute("backend_engineer", "Design REST API")
```

##### `track_tool(tool_name: str, context: Optional[str] = None)`
Track tool/capability usage.

**Example:**
```python
learning.track_tool("FastAPI", "Used for REST API endpoints")
learning.track_tool("PostgreSQL", "Used for data storage")
```

##### `track_decision(decision: str, rationale: Optional[str] = None)`
Track decision made during execution.

**Example:**
```python
learning.track_decision(
    "Use async/await for I/O operations",
    "Better performance for concurrent requests"
)
```

##### `track_blocker(blocker: str, resolution: Optional[str] = None)`
Track obstacles encountered.

**Example:**
```python
learning.track_blocker(
    "Connection pool sizing",
    "Researched PostgreSQL docs and best practices"
)
```

##### `track_output(output_path: str, description: Optional[str] = None)`
Track files/artifacts created.

**Example:**
```python
learning.track_output("api/main.py", "Main API implementation (450 lines)")
learning.track_output("api/models.py", "SQLAlchemy models")
```

##### `track_metrics(**kwargs)`
Track quality metrics.

**Metrics:**
- `test_coverage`: 0-100 (percentage)
- `code_quality_score`: 0-10 (float)
- `performance_latency_ms`: milliseconds
- `lines_of_code`: count

**Example:**
```python
learning.track_metrics(
    test_coverage=92,
    code_quality_score=8.7,
    lines_of_code=750,
    performance_latency_ms=35
)
```

##### `post_execute(agent_id: str, status: str = "completed", result: Optional[Dict] = None) → Dict`
End execution and trigger learning cycle.

**Returns:** Learning result with:
- `success`: bool
- `agent_id`: str
- `spec_version`: int
- `learnings`: dict
- `changes`: str (e.g., "+2 tools, +3 capabilities")
- `governance_note`: Optional[str]

**Example:**
```python
result = learning.post_execute("backend_engineer")
if result["success"]:
    print(f"✓ Spec v{result['spec_version']}")
    print(f"  Changes: {result['changes']}")
```

##### `get_agent_stats(agent_id: str) → Dict`
Get execution statistics.

**Example:**
```python
stats = learning.get_agent_stats("backend_engineer")
print(f"Total executions: {stats['total_executions']}")
print(f"Most used tools: {list(stats['tools_frequency'].keys())[:5]}")
```

##### `get_agent_evolution(agent_id: str) → Dict`
Get evolution summary across versions.

**Example:**
```python
evolution = learning.get_agent_evolution("backend_engineer")
print(f"Versions: {evolution['total_versions']}")
print(f"Tools growth: +{evolution['evolution']['tools_growth']}")
```

### AgentSupport Class

Lower-level API used by LearningIntegration.

```python
support = AgentSupport(company_dir)

# Execution tracking
exec_id = support.track_execution_start(agent_id, task)
support.track_execution_tool(tool, context)
support.track_execution_decision(decision, rationale)
support.track_execution_blocker(blocker, resolution)
support.track_execution_output(path, description)
support.track_execution_metrics(**metrics)

# Learning cycle
result = support.end_execution_and_learn(agent_id, status="completed")

# Analysis
stats = support.get_agent_stats(agent_id)
evolution = support.get_agent_evolution(agent_id)
history = support.get_spec_history(agent_id)
diff = support.compare_spec_versions(agent_id, v1, v2)
```

---

## File Structure

```
company/
├── agents/
│   ├── backend_engineer_agent.yaml      (current spec, auto-updated)
│   ├── frontend_engineer_agent.yaml
│   ├── ...
│   │
│   ├── .execution_logs/                 (execution telemetry)
│   │   ├── exec_backend_engineer_1705329000000.json
│   │   ├── exec_backend_engineer_1705329060000.json
│   │   └── ...
│   │
│   ├── .history/                        (version history)
│   │   ├── backend_engineer_agent_v1.yaml
│   │   ├── backend_engineer_agent_v2.yaml
│   │   ├── backend_engineer_agent_v3.yaml
│   │   └── ...
│   │
│   └── .learning_reports/               (analysis reports)
│       ├── backend_engineer_20250115_103000.md
│       ├── backend_engineer_20250115_110500.md
│       └── ...
│
├── intent_mapping.yaml                  (auto-updated with specializations)
├── agent_support.py                     (core integration layer)
├── execution_tracker.py                 (telemetry capture)
├── reflection_agent.py                  (pattern analysis)
├── autonomous_spec_manager.py            (versioning & updates)
├── learning_integration.py               (external integration)
├── agent_orchestrator.py                (integrated orchestrator)
└── LEARNING_INTEGRATION_GUIDE.md         (this file)
```

---

## Governance & Safety

### Automatic Review Triggers

Specs are flagged for review if they exceed thresholds:

```python
if version_diff >= 3:
    # Major change - requires review
    governance_note = "⚠ Review Required: Major version change (3+ versions)"

if len(capabilities_added) > 5:
    # Many new capabilities
    governance_note = "⚠ Review Required: Adding 5+ new capabilities"

if len(tools_added) > 8:
    # Many new tools
    governance_note = "⚠ Review Required: Adding 8+ new tools"
```

### Spec Versioning

All changes are automatically versioned:

```
v1 (initial)
├─ v2 (after 1st execution)
├─ v3 (after 2nd execution)
├─ v4 (after 3rd execution)
└─ v5 (after 4th execution) ← REQUIRES REVIEW (major change)
```

Rollback is always possible:

```python
learning.rollback_spec("backend_engineer", target_version=3)
# Spec restored to v3, with v5 archived
```

---

## Monitoring & Analysis

### Get Learning Reports

Reports are automatically saved after each execution:

```
company/agents/.learning_reports/
└── backend_engineer_20250115_103000.md

Learning Report: backend_engineer

Summary
- Executions Analyzed: 1
- Success Rate: 100.0%
- Specialization: None

Discoveries
### New Tools
- asyncio
- connection_pool_manager

### New Capabilities
- Async Request Handling
- Connection Pooling

### Patterns Emerged
- Use async/await with connection pooling

Performance Baseline
- Avg Duration: 180.0s
- Avg Test Coverage: 92%
- Avg Code Quality: 8.7/10

Blockers to Address
- Connection pool sizing (100%): Document solution and create guide

Changes Made
- +2 tools, +2 capabilities
- Requires Review: No
```

### Query Agent Evolution

```python
# Get full evolution data
evolution = learning.get_agent_evolution("backend_engineer")

# Print summary
print(f"Versions: {evolution['total_versions']}")
print(f"Tools: +{evolution['evolution']['tools_growth']}")
print(f"Capabilities: +{evolution['evolution']['capabilities_growth']}")
print(f"Specialization: {evolution['evolution']['specialization']}")
print(f"Quality: {evolution['evolution']['quality_improvement']}")
```

### View Execution History

```python
stats = learning.get_agent_stats("backend_engineer")

print(f"Total Executions: {stats['total_executions']}")
print(f"Success Rate: {stats['successful_executions']}/{stats['total_executions']}")
print(f"Tools Used (by frequency): {stats['tools_frequency']}")
print(f"Common Blockers: {[b['blocker'] for b in stats['common_blockers']]}")
print(f"Avg Duration: {stats['avg_duration_seconds']:.1f}s")
print(f"Code Quality: {stats['avg_code_quality']:.1f}/10")
```

---

## Integration Checklist

- [x] ExecutionTracker captures execution telemetry
- [x] ReflectionAgent analyzes patterns and learnings
- [x] AutonomousSpecManager versions and updates specs
- [x] Agent orchestrator integrated with learning system
- [x] LearningIntegration provides external integration point
- [x] Pre-execution hook (track_execution_start)
- [x] Post-execution hook (end_execution_and_learn)
- [x] Governance checks with review thresholds
- [x] Intent mapping updates on specialization
- [x] Delegation prompt refresh on spec change
- [x] Console logging: "[Autonomous Learning] Spec regeneration completed for {agent_id}, now at v{version}"
- [x] Rollback capability for bad updates
- [x] Learning reports and audit trails

---

## Next Steps for Implementation

### 1. Test with Agent Orchestrator

```bash
cd company
python3 agent_orchestrator.py
# Watch console for: [Autonomous Learning] Spec regeneration completed...
```

### 2. Integrate with External Agents

Use `LearningIntegration` in:
- Claude integration
- Copilot integration
- Custom agent runners
- REST API handlers

### 3. Monitor Evolution

Check `company/agents/.learning_reports/` for detailed analysis.

### 4. Implement Approval Workflow

Current system allows updates but flags major changes. Next phase:
- Create approval queue for governance review
- Implement notification system
- Add human approval before applying major updates

### 5. Build Metrics Dashboard

Create dashboard showing:
- Agent evolution across versions
- Tool and capability adoption
- Quality improvements
- Specialization areas
- Common blockers

---

## Troubleshooting

### Learning system not initialized

```python
if not learning.is_available():
    print("Check company_dir path and ensure dependencies are installed")
```

### Execution logs not appearing

```
Check: company/agents/.execution_logs/
Make sure ExecutionTracker has write permissions
```

### Specs not updating

1. Verify execution completed successfully (status="completed")
2. Check if changes meet governance thresholds
3. Review learning_reports for analysis output
4. Check agent_support initialization

### Rollback needed

```python
learning.rollback_spec("agent_id", target_version=N)
# Spec restored, intention_mapping updated, prompts regenerated
```

---

## Example: Complete Integration

```python
#!/usr/bin/env python3
from learning_integration import LearningIntegration

def main():
    # Initialize learning system
    learning = LearningIntegration("./company")
    
    if not learning.is_available():
        print("❌ Learning system not available")
        return
    
    # Execute with learning
    agent_id = "backend_engineer"
    task = "Design REST API for user management"
    
    print(f"[Agent] {agent_id} working on: {task}")
    
    # Pre-execution
    exec_id = learning.pre_execute(agent_id, task)
    print(f"✓ Started tracking: {exec_id}")
    
    # Simulate execution with tracking
    learning.track_tool("FastAPI", "Web framework")
    learning.track_tool("PostgreSQL", "Database")
    learning.track_tool("Pydantic", "Validation")
    
    learning.track_decision("Use async/await", "Better performance")
    learning.track_decision("Implement JWT auth", "Security standard")
    
    learning.track_blocker("Database migration", "Used SQLAlchemy migrations")
    
    learning.track_output("user_api.py", "User API endpoints")
    learning.track_output("models.py", "SQLAlchemy models")
    
    learning.track_metrics(
        test_coverage=95,
        code_quality_score=9.0,
        lines_of_code=850,
        performance_latency_ms=25
    )
    
    # Post-execution with automatic learning
    result = learning.post_execute(agent_id, status="completed")
    
    print(f"\n✓ Learning cycle completed:")
    print(f"  Version: {result['spec_version']}")
    print(f"  Changes: {result['changes']}")
    if result['learnings']['specialization']:
        print(f"  Specialization: {result['learnings']['specialization']}")
    
    # Show evolution
    evolution = learning.get_agent_evolution(agent_id)
    print(f"\nEvolution Summary:")
    print(f"  Total versions: {evolution['total_versions']}")
    print(f"  Tools growth: +{evolution['evolution']['tools_growth']}")
    print(f"  Capabilities growth: +{evolution['evolution']['capabilities_growth']}")

if __name__ == "__main__":
    main()
```

---

## Support

For issues or questions:
1. Check execution logs in `company/agents/.execution_logs/`
2. Review learning reports in `company/agents/.learning_reports/`
3. Verify spec versions in `company/agents/.history/`
4. Check `intent_mapping.yaml` for specialization entries
