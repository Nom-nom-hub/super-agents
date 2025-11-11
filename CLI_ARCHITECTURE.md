# Super-Agents CLI - Architecture

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         USER TERMINAL                               │
│                     (bash/zsh/powershell/cmd)                       │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                    python3 cli.py init
                             │
                    ┌────────▼────────┐
                    │   cli.py        │
                    │  (Click Entry)  │
                    └────────┬────────┘
                             │
                    ┌────────▼────────────────┐
                    │ Check HAS_RICH flag?   │
                    └────────┬───────────────┘
                             │
          ┌──────────────────┼──────────────────┐
          │                  │                  │
        YES                  │                 NO
          │                  │                  │
    ┌─────▼─────┐       ┌────▼─────┐      ┌──▼──────┐
    │  HAS_RICH │       │  Rich    │      │  Click  │
    │   TRUE    │       │ Available│      │ Prompts │
    └─────┬─────┘       └────┬─────┘      └──┬──────┘
          │                  │                │
          │         YES      │                │
          └──────────────────┴────────────────┘
                             │
                    ┌────────▼────────┐
                    │   ui.py         │
                    │ SuperAgentsUI   │
                    │  Instance       │
                    └────────┬────────┘
                             │
            ┌────────────────┼────────────────┐
            │                │                │
    ┌───────▼──────┐  ┌─────▼─────┐  ┌──────▼─────┐
    │show_header() │  │select_agent│  │select_     │
    │              │  │()          │  │script()    │
    │ - Clear      │  │            │  │            │
    │   screen     │  │ - Display  │  │ - Display  │
    │ - Print      │  │   menu     │  │   menu     │
    │   logo       │  │ - Arrow    │  │ - Arrow    │
    │ - Show       │  │   keys     │  │   keys     │
    │   subtitle   │  │ - Get      │  │ - Get      │
    │              │  │   input    │  │   input    │
    └──────────────┘  └─────┬─────┘  └──────┬─────┘
                            │               │
                    ┌───────┴───────┐
                    │               │
            ┌───────▼──────┐  ┌────▼──────┐
            │ Input from   │  │ Input from │
            │ User         │  │ User       │
            │ (Arrow keys) │  │ (Arrow key)│
            └───────┬──────┘  └────┬───────┘
                    │             │
                    │             │
            ┌───────▼──────────────┴───────┐
            │                              │
            │ agent_support.py             │
            │ - initialize_for_agent()     │
            │ - initialize_for_all()       │
            │                              │
            └───────┬──────────────────────┘
                    │
            ┌───────▼──────────┐
            │                  │
            │ Initialize       │
            │ Agents in        │
            │ ~/.xxx/ folders  │
            │                  │
            └───────┬──────────┘
                    │
            ┌───────▼──────────┐
            │                  │
            │ Run Optional     │
            │ Script (if       │
            │ selected)        │
            │                  │
            └───────┬──────────┘
                    │
            ┌───────▼──────────┐
            │                  │
            │ Show Success/    │
            │ Error Messages   │
            │                  │
            └───────┬──────────┘
                    │
                    │
            ┌───────▼──────────┐
            │                  │
            │ Return to        │
            │ Terminal Prompt  │
            │                  │
            └──────────────────┘
```

## Module Interaction

```
cli.py
├─ main entry point
├─ parses command-line arguments (--agent, --all, --script)
├─ imports SuperAgentsUI if rich available
├─ calls SuperAgentsUI.select_agent()    ← for interactive menu
├─ calls SuperAgentsUI.select_script()   ← for optional script menu
├─ calls agent_support.initialize_for_agent()
├─ calls agent_support.initialize_for_all_available()
└─ displays results via SuperAgentsUI

ui.py
├─ SuperAgentsUI class
├─ show_header()
│  ├─ console.clear()
│  ├─ print ASCII logo
│  └─ print subtitle
├─ select_agent(agents_dict)
│  ├─ show_header()
│  ├─ display agent list
│  └─ _show_menu() with arrow key input
├─ select_script(scripts_dict)
│  ├─ show_header()
│  ├─ display script list
│  └─ _show_menu() with arrow key input
├─ _show_menu(title, items, color_map)
│  ├─ handle arrow key navigation
│  ├─ fallback to numbered selection
│  └─ return selected value
├─ show_progress(message)
├─ show_success(message)
├─ show_error(message)
└─ show_info(message)

agent_support.py
├─ AgentSupport class
├─ initialize_for_agent(agent_id)
│  └─ creates config files for specific agent
├─ initialize_for_all_available()
│  └─ initializes all available agents
└─ ... other agent support methods
```

## Data Flow

### Interactive Mode

```
User runs: python3 cli.py init

    ↓

Check for rich library (HAS_RICH)

    ↓

If rich available:
  - Create SuperAgentsUI instance
  - Call ui.show_header() → display logo
  - Call ui.select_agent() → interactive menu
  - User navigates with arrow keys
  - User presses Enter
  - Return selected agent

    ↓

Initialize selected agent:
  - Call agent_support.initialize_for_agent(agent)
  - Show progress
  - Show success message

    ↓

Ask for optional script:
  - Call ui.select_script()
  - User selects or skips
  - If selected: execute script
  - Show result

    ↓

Exit with success code
```

### Non-Interactive Mode

```
User runs: python3 cli.py init --agent claude --script update-agent-context

    ↓

Parse arguments
- agent = "claude"
- script = "update-agent-context"

    ↓

Skip agent selection (agent specified)
Skip script selection (script specified)

    ↓

Initialize claude:
  - Call agent_support.initialize_for_agent("claude")
  - Show success

    ↓

Run update-agent-context script:
  - Execute script
  - Show result

    ↓

Exit with success code
```

## File Organization

```
super-agents/
│
├── company/
│   ├── cli.py ◄─────────── Main CLI (Click commands)
│   ├── ui.py ◄─────────── Beautiful UI module (Rich)
│   ├── agent_support.py ◄─ Agent initialization logic
│   ├── agent_registry.yaml ◄ Agent configuration
│   ├── agents/           ◄─ Agent specifications
│   │   ├── claude_agent.yaml
│   │   ├── copilot_agent.yaml
│   │   └── ...
│   │
│   ├── README_CLI.md ◄────────── Complete user guide
│   ├── QUICK_START.md ◄────────── Quick reference
│   ├── requirements-cli.txt ◄──── Dependencies
│   ├── install-cli-deps.sh ◄───── Unix installer
│   └── install-cli-deps.ps1 ◄──── Windows installer
│
├── scripts/
│   ├── update-agent-context.sh
│   └── update-agent-context.ps1
│
├── INIT_CLI_GUIDE.md ◄──────────── CLI guide
├── BEAUTIFUL_CLI_SUMMARY.md ◄───── Implementation details
└── CLI_ARCHITECTURE.md ◄────────── This file
```

## Class Diagram

```
┌─────────────────────────────────────┐
│         SuperAgentsUI               │
├─────────────────────────────────────┤
│ - console: Console                  │
│ - LOGO: str                         │
├─────────────────────────────────────┤
│ Methods:                            │
│ + __init__()                        │
│ + show_header()                     │
│ + select_agent(dict) -> str         │
│ + select_script(dict) -> str        │
│ + show_progress(str)                │
│ + show_success(str)                 │
│ + show_error(str)                   │
│ + show_info(str)                    │
│ - _show_menu(title, items) -> value │
│ - _fallback_menu(items) -> value    │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│         AgentSupport (existing)     │
├─────────────────────────────────────┤
│ Methods:                            │
│ + initialize_for_agent(str) -> bool │
│ + initialize_for_all_available()    │
│ + list_registered_agents() -> list  │
│ + get_agent_config(str) -> dict     │
│ + create_agent_context_file(str)    │
└─────────────────────────────────────┘
```

## Execution Flow (Sequence Diagram)

```
User          CLI              UI              AgentSupport
  │             │              │                   │
  ├─ init ─────>│              │                   │
  │             │              │                   │
  │             ├─ check rich ─┐                   │
  │             │              │ HAS_RICH=true     │
  │             │<─────────────┘                   │
  │             │              │                   │
  │             ├─ new UI ─────────────>│         │
  │             │                       │         │
  │             ├─ show_header ─────────────────>│ │
  │             │              │   (display)     │
  │             │              │<──────────────┘ │
  │             │              │                 │
  │             ├─ select_agent ────────────────>│ │
  │             │              │   (arrow keys)  │
  │  (navigate) │<─────────────────────────────┘
  │    ↑↓       │              │
  │            │              │
  │  (enter)   │<──────────────────────────────┘
  │             │              │ returns: "claude"
  │             │              │                   │
  │             ├─ initialize_for_agent ────────>│
  │             │                                │ (creates config)
  │             │                                │
  │             │                          (success)
  │             │<───────────────────────────────┤
  │             │                                │
  │             ├─ show_success ────────────────>│ │
  │             │              │   (display)     │
  │             │              │<──────────────┘ │
  │             │              │                   │
  │             ├─ select_script ────────────────>│ │
  │             │              │   (arrow keys)  │
  │  (select or skip)          │                 │
  │             │<─────────────────────────────┘
  │             │              │ returns: script  │
  │             │              │                   │
  │             ├─ execute script                │
  │             │              │                   │
  │             ├─ show_success                  │
  │             │              │                   │
  │             ├─ return ─────>│                   │
  │  (done)    │              │                   │
  │             │              │                   │
```

## Dependency Resolution

```
cli.py
├─ try: import rich.console
│  └─ if successful: HAS_RICH = True
│  └─ if fails: HAS_RICH = False
│
├─ try: from ui import SuperAgentsUI
│  └─ only if HAS_RICH is True
│
├─ try: import click
│  └─ required, exit if fails
│
├─ try: import questionary
│  └─ optional, used if available
│
└─ try: import tabulate
   └─ optional, for other commands


On __name__ == "__main__":
├─ Check each dependency
├─ Build list of missing deps
├─ For each missing:
│  └─ pip3 install {dep} || pip install {dep}
└─ Import and run CLI
```

## Terminal Support Matrix

```
┌────────────────┬──────────────┬──────────┬──────────────┐
│ Terminal       │ Arrow Keys   │ Colors   │ Mode         │
├────────────────┼──────────────┼──────────┼──────────────┤
│ bash (Unix)    │ ✓ Works      │ ✓ Full   │ Interactive  │
│ zsh (Mac)      │ ✓ Works      │ ✓ Full   │ Interactive  │
│ PowerShell 7+  │ ✓ Works      │ ✓ Full   │ Interactive  │
│ Windows CMD    │ ✗ Fallback   │ ✓ Basic  │ Numbered     │
│ SSH Terminal   │ ⚠ Varies     │ ⚠ Varies │ Numbered     │
│ IDE Terminal   │ ✓ Works      │ ✓ Full   │ Interactive  │
└────────────────┴──────────────┴──────────┴──────────────┘
```

## Performance Characteristics

```
Operation               Time      Notes
─────────────────────────────────────────────────────────
Initialize 1 agent      < 1s      File creation
Initialize 9 agents     < 5s      Sequential init
Show menu               instant    Immediate render
Navigate menu             0ms      Per key press
Display logo            < 100ms    First display
Load agent list         < 100ms    From YAML
```

---

For more information, see:
- README_CLI.md - User guide
- BEAUTIFUL_CLI_SUMMARY.md - Implementation details
- QUICK_START.md - Quick reference
