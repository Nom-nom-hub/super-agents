# Super-Agents CLI - Quick Start

## Installation (First Time)

```bash
cd company
bash install-cli-deps.sh    # Mac/Linux
# or
powershell -File install-cli-deps.ps1  # Windows
```

Or let the CLI auto-install on first run.

## Launch

```bash
python3 cli.py init
```

That's it! You'll see:

```
    ███████╗██╗   ██╗██████╗ ███████╗██████╗     █████╗  ██████╗ ███████╗███╗   ██╗████████╗███████╗
    ██╔════╝██║   ██║██╔══██╗██╔════╝██╔══██╗   ██╔══██╗██╔════╝ ██╔════╝████╗  ██║╚══██╔══╝██╔════╝
    ███████╗██║   ██║██████╔╝█████╗  ██████╔╝   ███████║██║  ███╗█████╗  ██╔██╗ ██║   ██║   █████╗  
    ╚════██║██║   ██║██╔═══╝ ██╔══╝  ██╔══██╗   ██╔══██║██║   ██║██╔══╝  ██║╚██╗██║   ██║   ██╔══╝  
    ███████║╚██████╔╝██║     ███████╗██║  ██║   ██║  ██║╚██████╔╝███████╗██║ ╚████║   ██║   ███████╗
    ╚══════╝ ╚═════╝ ╚═╝     ╚══════╝╚═╝  ╚═╝   ╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚═╝  ╚═══╝   ╚═╝   ╚══════╝

AICODE Labs - AI Agent Initialization

Select an Agent:
  ❯ claude          Claude Code
    copilot         GitHub Copilot
    ...

  Use ↑/↓ to navigate, Enter to select, Ctrl+C to cancel
```

## Controls

| Key    | What It Does |
| ------ | ------------ |
| ↑      | Move up      |
| ↓      | Move down    |
| Enter  | Select       |
| Ctrl+C | Cancel       |

## Commands

```bash
# Interactive mode (recommended)
python3 cli.py init

# Choose agent directly
python3 cli.py init --agent claude
python3 cli.py init --agent amp

# Initialize all agents
python3 cli.py init --all

# Auto-run script too
python3 cli.py init --agent claude --script update-agent-context

# Other commands
python3 cli.py detect        # Check available agents
python3 cli.py status        # System status
python3 cli.py list-agents   # List all super-agents
```

## Agents Available

- `claude` - Claude Code
- `copilot` - GitHub Copilot
- `amp` - Sourcegraph Amp
- `gemini` - Google Gemini CLI
- `cursor` - Cursor IDE
- `windsurf` - Windsurf IDE
- `q` - Amazon Q Developer CLI
- `qwen` - Alibaba Qwen Code
- `kilocode` - Kilo Code

## Scripts Available

- `update-agent-context` - Update agent context with latest info

## Troubleshooting

**Arrow keys don't work?**
→ Normal on Windows CMD. The CLI will ask for numbered input instead.

**Logo looks weird?**
→ Your terminal might need UTF-8. Try:

```bash
export LANG=en_US.UTF-8
python3 cli.py init
```

**Dependencies not installing?**

```bash
pip3 install click rich questionary tabulate
python3 cli.py init
```

**Still having issues?**
→ Check `README_CLI.md` for detailed troubleshooting.

## Examples

### Initialize Claude with arrow keys

```
1. Run: python3 cli.py init
2. Press: ↓ (down arrow)
3. Press: Enter (to select Claude)
4. Done! Press ↓ → Enter to skip script, or select one
```

### Quick initialization for multiple developers

```bash
# Run once per machine
python3 cli.py init --all --script update-agent-context
```

### Add to your setup script

```bash
#!/bin/bash
cd company
python3 cli.py init --all
```

______________________________________________________________________

**Full documentation:** See `README_CLI.md` and `INIT_CLI_GUIDE.md`
