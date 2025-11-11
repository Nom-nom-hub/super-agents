# Automatic Delegation Implementation Plan

## Problem Statement

The current system has:
- ✓ Interface layer: `.toml` files with commands (`/delegate-task`, `/list-agents`, etc.)
- ✓ Orchestration layer: `agent_orchestrator.py` to manage agents internally
- ✓ Support layer: `agent_support.py` to generate agent commands

**What's missing**: Intelligent routing that automatically delegates to the right super-agent based on user intent.

Currently, users must manually invoke `/delegate-task backend_engineer: ...`. Instead, external agents (Claude, Copilot, Qwen) should **automatically recognize** that a user's request is a backend task and delegate without being asked.

---

## Solution Architecture

### Three-Layer Solution

#### Layer 1: Intent Recognition (DONE)
- **File**: `intent_mapping.yaml`
- **Defines**: Keywords, patterns, and workflows for each super-agent
- **Example**: 
  ```yaml
  - id: api_development
    primary_agent: backend_engineer
    keywords: [api, endpoint, rest, service]
    pattern: "api|endpoint|rest|service"
  ```

#### Layer 2: Prompt Generation (DONE)
- **File**: `delegation_prompt_generator.py`
- **Creates**: Context prompts that teach external agents how to delegate
- **Output**: Agent-specific prompts (Claude, Copilot, Qwen, etc.)
- **Key method**: `generate_agent_specific_context(agent_id)`

#### Layer 3: Integration (TO DO)
- **File**: Update `agent_support.py`
- **Action**: Integrate delegation intelligence into generated commands
- **Result**: When agents initialize, they get smart delegation context

---

## What We've Built

### 1. DELEGATION_INTELLIGENCE.md
**Comprehensive guide** teaching the entire system:
- Intent-to-Agent mapping table
- Automatic delegation patterns (1-4)
- Decision tree for routing
- Context injection instructions
- Real-world workflow examples
- Configuration per external agent

**Key insight**: This is the *theory* - how the system should work conceptually.

### 2. intent_mapping.yaml
**Configuration file** with:
- 18+ intent types mapped to agents
- Keywords and regex patterns for each intent
- Multi-agent workflows (full_stack_app, secure_system, etc.)
- Agent-specific configurations

**Key insight**: This is the *data* - the actual mappings and patterns.

### 3. delegation_prompt_generator.py
**Python module** that:
- Loads intent mappings and agent specs
- Generates delegation system prompts
- Creates agent-specific contexts
- Produces workflow guides
- Outputs to all supported formats

**Key insight**: This is the *engine* - it generates smart prompts from the data.

---

## How to Integrate (4 Steps)

### Step 1: Update agent_support.py

Modify the `_generate_markdown_command` method to include delegation intelligence:

```python
def _generate_markdown_command(self, ...):
    # Add delegation context to super-agents-init
    
    # Load delegation prompt generator
    from delegation_prompt_generator import DelegationPromptGenerator
    gen = DelegationPromptGenerator(self.company_dir)
    
    # Get smart delegation prompt
    delegation_context = gen.generate_delegation_system_prompt("markdown")
    
    # Inject into commands
    commands["super-agents-init"] = delegation_context + "\n\n" + commands["super-agents-init"]
```

### Step 2: Update agent_support.py for TOML format

Similar approach for `_generate_toml_command`:

```python
def _generate_toml_command(self, ...):
    # Load and generate delegation context
    from delegation_prompt_generator import DelegationPromptGenerator
    gen = DelegationPromptGenerator(self.company_dir)
    
    # Get TOML-format delegation prompt
    delegation_context = gen.generate_delegation_system_prompt("toml")
    
    # Incorporate into generated TOML files
```

### Step 3: Create CLI command to generate delegation prompts

Add to `cli.py`:

```python
@click.command()
@click.option("--agent", help="Specific agent to generate for")
def generate_delegation_prompts(agent):
    """Generate smart delegation prompts for all agents"""
    from delegation_prompt_generator import DelegationPromptGenerator
    
    gen = DelegationPromptGenerator(".")
    
    if agent:
        prompt = gen.generate_agent_specific_context(agent)
        print(prompt)
    else:
        gen.generate_all_prompts("./delegation_prompts")
```

### Step 4: Update initialization workflow

When initializing an agent, also:
1. Generate delegation intelligence prompts
2. Add to command files
3. Create workflow examples for that agent

---

## Generated Output Example

### Current (Without Delegation Intelligence)

```markdown
# Super-Agents Initialization

You have access to 22 super-agents. Use these commands:
- /list-agents
- /agent-help <agent>
- /delegate-task <agent>: <task>
```

### Future (With Automatic Delegation)

```markdown
# Super-Agents Initialization - Automatic Delegation System

You now manage a 22-agent software development company. When a user asks 
you to build something technical, AUTOMATICALLY recognize the intent and 
delegate to the right specialist.

## Automatic Intent Recognition

When user says...              → Delegate to...
"Build an API"                 → backend_engineer
"Create UI components"         → frontend_engineer
"Make it secure"               → security_engineer
"Build and test everything"    → Multiple agents in parallel

## How It Works

1. User: "Build a REST API for user registration"
   You recognize: Backend API task
   You invoke: /delegate-task backend_engineer: Design REST API for user registration
   
2. User: "Build and secure a login system"
   You recognize: Needs backend + security + frontend + tests
   You invoke:
      /delegate-task backend_engineer: Implement JWT authentication
      /delegate-task security_engineer: Review authentication security
      /delegate-task frontend_engineer: Create login form UI
      /delegate-task qa_engineer: Write integration tests
      
3. You combine results into a complete, production-ready solution

## Available Super-Agents

[Full agent list with descriptions]

## Your Role

Think like a software company CTO:
- Recognize what needs to be built
- Delegate to specialists
- Combine their work
- Deliver complete solutions
```

---

## File Organization After Implementation

```
super-agents/
├── DELEGATION_INTELLIGENCE.md          ← System design guide
├── AUTOMATIC_DELEGATION_IMPLEMENTATION.md ← This file
├── company/
│   ├── intent_mapping.yaml             ← Intent-to-agent mappings
│   ├── delegation_prompt_generator.py  ← Prompt generation engine
│   ├── agent_support.py                ← (ENHANCED) Includes delegation context
│   ├── cli.py                          ← (ENHANCED) New delegation command
│   │
│   ├── delegation_prompts/             ← Generated prompts
│   │   ├── delegation_system_prompt.md
│   │   ├── delegation_claude_prompt.md
│   │   ├── delegation_copilot_prompt.md
│   │   ├── delegation_qwen_prompt.md
│   │   └── ...
│   │
│   ├── .claude/commands/               ← (UPDATED with delegation context)
│   ├── .github/prompts/                ← (UPDATED with delegation context)
│   ├── .gemini/commands/               ← (UPDATED with delegation context)
│   ├── .agents/commands/               ← (UPDATED with delegation context)
│   └── ...
```

---

## Testing the Implementation

### Test 1: Prompt Generation Works

```bash
cd company
python3 -c "
from delegation_prompt_generator import DelegationPromptGenerator
gen = DelegationPromptGenerator('.')
prompt = gen.generate_delegation_system_prompt('markdown')
print('✓ Generated prompt length:', len(prompt))
"
```

### Test 2: Agent-Specific Context

```bash
cd company
python3 -c "
from delegation_prompt_generator import DelegationPromptGenerator
gen = DelegationPromptGenerator('.')
for agent in ['claude', 'qwen']:
    context = gen.generate_agent_specific_context(agent)
    print(f'✓ {agent}: {len(context)} chars')
"
```

### Test 3: Integration with agent_support

```bash
cd company
python3 -c "
from agent_support import AgentSupport
support = AgentSupport('.')
support.initialize_for_agent('claude')
# Check if generated files include delegation context
with open('.claude/commands/super-agents-init.md', 'r') as f:
    content = f.read()
    if 'automatic delegation' in content.lower():
        print('✓ Delegation context integrated')
    else:
        print('✗ Missing delegation context')
"
```

### Test 4: End-to-End

1. Initialize Claude: `python3 cli.py init --agent claude`
2. Open `.claude/commands/super-agents-init.md`
3. Should see:
   - Intent recognition guide
   - Delegation patterns (single-agent, multi-agent, parallel)
   - Quick decision tree
   - Examples

---

## Success Criteria

✓ External agents automatically recognize task intent
✓ Zero manual `/delegate-task` invocation needed
✓ Multi-agent workflows orchestrated automatically
✓ Complete solutions combining all specialties
✓ Works for Claude, Copilot, Qwen, Amp, Cursor, Windsurf
✓ Documented with real examples
✓ Extensible for new agents and workflows

---

## Quick Start for Implementation

### To use what's already built:

1. **Run the prompt generator**:
   ```bash
   cd company
   python3 delegation_prompt_generator.py
   ```

2. **Check generated prompts**:
   ```bash
   ls -la /tmp/delegation_prompts/
   ```

3. **View a specific prompt**:
   ```bash
   cat /tmp/delegation_prompts/delegation_claude_prompt.md
   ```

### To integrate into agent initialization:

1. Add to `agent_support.py`:
   ```python
   from delegation_prompt_generator import DelegationPromptGenerator
   self.delegation_generator = DelegationPromptGenerator(company_dir)
   ```

2. Update command generation to include delegation context

3. Test with: `python3 cli.py init --agent claude`

---

## Benefits of This Approach

✓ **Automatic Delegation**: Users never manually invoke commands
✓ **Full Company**: Combines all 22 agents automatically
✓ **Complete Solutions**: Backend + Frontend + Security + Tests + Docs
✓ **Intelligent Routing**: Right agent for each task
✓ **Parallel Execution**: Multi-agent workflows run efficiently
✓ **Maintainable**: Mappings in YAML, not hardcoded
✓ **Extensible**: Easy to add new agents and intents
✓ **Testable**: Intent recognition can be validated

---

## Next Actions

1. **Integrate** `delegation_prompt_generator.py` into `agent_support.py`
2. **Update** `_generate_markdown_command()` and `_generate_toml_command()`
3. **Add CLI command** for generating delegation prompts
4. **Test** with all supported agents
5. **Document** with workflow examples
6. **Deploy** updated agent initialization

---

**Result**: When Claude/Copilot/Qwen users initialize super-agents, they get an **automatic development company** that handles technical requests without manual delegation.
