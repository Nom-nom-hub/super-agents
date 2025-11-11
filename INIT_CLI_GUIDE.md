# Beautiful Interactive CLI Guide

The `init` command features a stunning custom UI with ASCII logo, arrow key navigation, and beautiful terminal output.

## Features

### 1. 🎨 Custom UI with ASCII Logo
- Beautiful Super-Agents ASCII art header
- Rich terminal colors and formatting
- Clean panel-based output for success/error messages
- Professional-grade terminal UI

### 2. ⌨️ Arrow Key Navigation
- Full arrow key support (↑/↓)
- Smooth selection with visual feedback
- Enter to confirm, Ctrl+C to cancel
- Graceful fallback to numbered selection on unsupported terminals

### 3. 🎯 Interactive Agent Selection
- Navigate agents with arrow keys
- Color-coded display (green for agents, yellow for "All")
- Select specific agent or initialize all at once
- Clear visual selection indicator (❯)

### 4. 📝 Interactive Script Selection
- Same beautiful UI for script selection
- Optional scripts - easy to skip
- Automatic platform detection (.sh vs .ps1)
- Progress feedback during execution

## Usage

### Interactive Mode (Recommended)
```bash
python3 cli.py init
```

**What you'll see:**
```
    ███████╗██╗   ██╗██████╗ ███████╗██████╗     █████╗  ██████╗ ███████╗███╗   ██╗████████╗███████╗
    ██╔════╝██║   ██║██╔══██╗██╔════╝██╔══██╗   ██╔══██╗██╔════╝ ██╔════╝████╗  ██║╚══██╔══╝██╔════╝
    ███████╗██║   ██║██████╔╝█████╗  ██████╔╝   ███████║██║  ███╗█████╗  ██╔██╗ ██║   ██║   █████╗  
    ╚════██║██║   ██║██╔═══╝ ██╔══╝  ██╔══██╗   ██╔══██║██║   ██║██╔══╝  ██║╚██╗██║   ██║   ██╔══╝  
    ███████║╚██████╔╝██║     ███████╗██║  ██║   ██║  ██║╚██████╔╝███████╗██║ ╚████║   ██║   ███████╗
    ╚══════╝ ╚═════╝ ╚═╝     ╚══════╝╚═╝  ╚═╝   ╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚═╝  ╚═══╝   ╚═╝   ╚══════╝

Select an Agent:
  ❯ claude          Claude Code
    copilot         GitHub Copilot
    amp             Amp
    gemini          Gemini CLI
    cursor          Cursor
    windsurf        Windsurf
    q               Amazon Q Developer CLI
    qwen            Qwen Code
    kilocode        Kilo Code
    all             Initialize All Agents

  Use ↑/↓ to navigate, Enter to select, Ctrl+C to cancel
```

### Direct Agent + Script
```bash
python3 cli.py init --agent claude --script update-agent-context
```
Full automation, no prompts

### Initialize All Agents
```bash
python3 cli.py init --all
```
Then prompts for optional script

### Select Agent Only
```bash
python3 cli.py init --agent claude
```
Then prompts for optional script

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

- `update-agent-context` - Updates agent context files

## Dependencies

Automatically installed on first run:
- `click` - CLI framework (required)
- `rich` - Beautiful terminal UI
- `questionary` - Alternative interactive selection (optional)
- `tabulate` - Table formatting

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| ↑ | Move up in menu |
| ↓ | Move down in menu |
| Enter | Select item |
| Ctrl+C | Cancel operation |

## Architecture

The CLI uses a modular design:
- `cli.py` - Main CLI with Click commands
- `ui.py` - Custom beautiful UI with SuperAgentsUI class
- `agent_support.py` - Agent initialization logic

The UI gracefully degrades on unsupported terminals (Windows cmd, etc.) to numbered selection.
