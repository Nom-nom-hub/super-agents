#!/usr/bin/env python3
"""
AICODE Labs - Super-Agents CLI

Command-line interface for initializing and managing multi-agent support.
Inspired by GitHub Spec Kit's Specify CLI.
"""

import os
import sys
from typing import Any, Dict, List, Optional, Tuple

try:
    import click
except ImportError:
    print("Error: 'click' is required. Install with: pip3 install click")
    sys.exit(1)

try:
    from tabulate import tabulate
except ImportError:
    # Fallback if tabulate not available
    def tabulate(
        data: List[List[str]],
        headers: Optional[List[str]] = None,
        tablefmt: Optional[str] = None,
    ) -> None:
        if headers:
            print("  " + "  ".join(f"{h:20}" for h in headers))
            print("  " + "-" * (22 * len(headers)))
        for row in data:
            print("  " + "  ".join(f"{str(v):20}" for v in row))


try:
    from rich.console import Console

    HAS_RICH = True
except ImportError:
    HAS_RICH = False

try:
    import questionary
except ImportError:
    questionary = None

try:
    # For installed package
    from ..agent_support import AgentSupport
except ImportError:
    # For development/standalone execution
    import os
    import sys

    # Add the super_agents directory to the path
    super_agents_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, super_agents_dir)
    from agent_support import AgentSupport

# Import custom UI if rich is available
if HAS_RICH:
    try:
        from .ui import SuperAgentsUI
    except ImportError:
        # For development/standalone execution
        import os
        import sys

        cli_dir = os.path.dirname(os.path.abspath(__file__))
        sys.path.insert(0, cli_dir)
        from ui import SuperAgentsUI


@click.group()
def cli() -> None:
    """AICODE Labs Super-Agents CLI"""
    pass


@cli.command()
def detect() -> None:
    """Detect available AI agents on system"""
    # Set agents_dir to the current working directory for installed tools
    agents_dir: str = os.getcwd()

    # If registry not found in current directory, try super_agents subdirectory
    registry_path = os.path.join(agents_dir, "agent_registry.yaml")
    if not os.path.exists(registry_path):
        potential_agent_dir = os.path.join(agents_dir, "super_agents")
        if os.path.exists(potential_agent_dir):
            agents_dir = potential_agent_dir

    support: AgentSupport = AgentSupport(agents_dir)
    available: Dict[str, bool] = support.detect_available_agents()

    print("\n📊 AI Agent Detection Report\n")
    print("=" * 60)

    data: List[List[str]] = []
    for agent_id, config in sorted(support.registry.get("agents", {}).items()):
        status = "✓ Available" if available.get(agent_id) else "✗ Not Found"
        cli_tool = config.get("cli_tool", "IDE-based")
        data.append([agent_id, config["name"], cli_tool, status])

    headers: List[str] = ["Agent ID", "Name", "CLI Tool / Type", "Status"]
    print(tabulate(data, headers=headers, tablefmt="grid"))

    available_agents: List[str] = [a for a, v in available.items() if v]
    print(f"\n✓ Found {len(available_agents)} available agents")

    if available_agents:
        print(f"\nAvailable: {', '.join(available_agents)}\n")
    else:
        print("\nℹ️  No CLI agents detected. Install agents or use IDE-based ones.\n")


def _load_scripts(scripts_dir: str) -> Dict[str, str]:
    """Load available scripts from scripts directory"""
    scripts: Dict[str, str] = {}
    if os.path.exists(scripts_dir):
        for filename in os.listdir(scripts_dir):
            if filename.endswith((".sh", ".ps1")):
                name = filename.rsplit(".", 1)[0]
                scripts[name] = os.path.join(scripts_dir, filename)
    return scripts


def _select_agent_interactive_ui(
    support: AgentSupport, ui: Optional[SuperAgentsUI]
) -> Tuple[Optional[str], bool]:
    """Handle agent selection using rich UI."""
    registered = support.list_registered_agents()
    agents_dict = {
        agent_id: support.get_agent_config(agent_id) for agent_id in registered
    }

    # Use beautiful custom UI
    selection = ui.select_agent(agents_dict)
    if selection is None:
        return None, False
    elif selection == "all":
        return None, True
    else:
        return selection, False


def _select_agent_interactive_questionary(
    support: AgentSupport,
) -> Tuple[Optional[str], bool]:
    """Handle agent selection using questionary."""
    registered = support.list_registered_agents()
    choices = [
        {
            "name": f"{agent_id} ({support.get_agent_config(agent_id)['name']})",
            "value": agent_id,
        }
        for agent_id in registered
    ]
    choices.append({"name": "All agents", "value": "all"})

    selection = questionary.select("Select an agent:", choices=choices).ask()

    if selection is None:  # User cancelled
        return None, False
    elif selection == "all":
        return None, True
    else:
        return selection, False


def _select_agent_interactive_click(
    support: AgentSupport,
) -> Tuple[Optional[str], bool]:
    """Handle agent selection using click prompts."""
    registered = support.list_registered_agents()
    agent_list = list(registered)

    click.echo("\n🤖  Super-Agents Initialization\n")
    click.echo("Select an agent:")
    for i, a in enumerate(agent_list, 1):
        config = support.get_agent_config(a)
        click.echo(f"  {i}. {a} ({config['name']})")
    click.echo(f"  {len(agent_list) + 1}. All agents")
    click.echo("  0. Cancel\n")

    choice = click.prompt("Enter your choice", type=int)

    if choice == 0:
        return None, False
    elif choice == len(agent_list) + 1:
        return None, True
    elif 1 <= choice <= len(agent_list):
        return agent_list[choice - 1], False
    else:
        click.secho("Invalid choice", fg="red")
        return None, False


def _select_agent_interactive(
    support: AgentSupport, ui: Optional[SuperAgentsUI]
) -> Tuple[Optional[str], bool]:
    """Handle interactive agent selection using available UI options."""

    registered = support.list_registered_agents()
    if not registered:
        return None, False  # No agents to select

    if ui:
        return _select_agent_interactive_ui(support, ui)
    elif questionary:
        return _select_agent_interactive_questionary(support)
    else:
        return _select_agent_interactive_click(support)


def _initialize_agents(
    support: AgentSupport,
    agent: Optional[str],
    init_all: bool,
    ui: Optional[SuperAgentsUI],
) -> bool:
    """Handle agent initialization based on selection."""
    if init_all:
        if ui:
            ui.show_progress("Initializing all agents")
        else:
            click.echo("\nInitializing all agents...")

        count = support.initialize_for_all_available()

        if ui:
            ui.show_success(f"Initialized {count} agents successfully!")
        else:
            click.secho(
                f"\n✓ Initialized {count} agents successfully!", fg="green", bold=True
            )
        return True
    elif agent:
        if ui:
            ui.show_progress(f"Initializing {agent}")
        else:
            click.echo(f"\nInitializing {agent}...")

        success = support.initialize_for_agent(agent, output_dir=os.getcwd())

        if success:
            if ui:
                ui.show_success(f"Initialized {agent} successfully!")
            else:
                click.secho(
                    f"\n✓ Initialized {agent} successfully!", fg="green", bold=True
                )
        else:
            if ui:
                ui.show_error(f"Failed to initialize {agent}")
            else:
                click.secho(f"\n✗ Failed to initialize {agent}", fg="red", bold=True)
            sys.exit(1)
        return success
    return False


def _select_script_interactive(
    scripts: Dict[str, str], ui: Optional[SuperAgentsUI]
) -> Optional[str]:
    """Handle interactive script selection using available UI options."""
    if not scripts:
        return None

    if ui:
        return ui.select_script(scripts)
    elif questionary:
        # Use questionary for interactive script selection if available
        choices = [
            {"name": script_name, "value": script_name}
            for script_name in sorted(scripts.keys())
        ]
        choices.insert(
            0, {"name": "Skip", "value": None}
        )  # Add "Skip" option at the beginning

        return questionary.select("Select a script (optional):", choices=choices).ask()
    else:
        click.echo("\nAvailable scripts:")
        script_list = sorted(scripts.keys())
        for i, script_name in enumerate(script_list, 1):
            click.echo(f"  {i}. {script_name}")
        click.echo("  0. Skip\n")

        script_choice = click.prompt("Select a script", type=int, default=0)

        if 1 <= script_choice <= len(script_list):
            return script_list[script_choice - 1]
        return None


def _execute_script(script: str, ui: Optional[SuperAgentsUI]) -> None:
    """Execute the selected script."""
    scripts_dir = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "scripts"
    )
    scripts = _load_scripts(scripts_dir)

    if script in scripts:
        script_path = scripts[script]

        if ui:
            ui.show_progress(f"Running {script}")
        else:
            click.echo(f"\nRunning {script}...")

        import subprocess

        # Use subprocess instead of os.system to avoid shell injection
        if script.endswith(".sh"):
            result = subprocess.run(["bash", script_path], check=False)
        else:
            result = subprocess.run(["powershell", "-File", script_path], check=False)

        if result == 0:
            if ui:
                ui.show_success("Script executed successfully")
            else:
                click.secho("\n✓ Script executed successfully", fg="green", bold=True)
        else:
            if ui:
                ui.show_error("Script execution failed")
            else:
                click.secho("\n✗ Script execution failed", fg="red", bold=True)
    else:
        if ui:
            ui.show_error(f"Script '{script}' not found")
        else:
            click.secho(f"✗ Script '{script}' not found", fg="red")


@cli.command()
@click.option(
    "--agent",
    "-a",
    help="Specific agent to initialize (claude, copilot, amp, gemini, cursor, etc.)",
)
@click.option(
    "--all", "init_all", is_flag=True, help="Initialize for all available agents"
)
@click.option("--script", "-s", help="Run a script after initialization")
@click.option("--project", "-p", help="Project context to use for initialization")
def init(
    agent: Optional[str], init_all: bool, script: Optional[str], project: Optional[str]
) -> None:
    """Initialize super-agents for AI agents with comprehensive context files"""
    # Set agents_dir to the current working directory for installed tools
    # This ensures files are created where the user runs the command
    agents_dir = os.getcwd()

    # If registry not found in current directory, try super_agents subdirectory
    registry_path = os.path.join(agents_dir, "agent_registry.yaml")
    if not os.path.exists(registry_path):
        potential_agent_dir = os.path.join(agents_dir, "super_agents")
        if os.path.exists(potential_agent_dir):
            agents_dir = potential_agent_dir

    support = AgentSupport(agents_dir)
    ui = SuperAgentsUI() if HAS_RICH else None

    # Handle agent selection if not specified
    if not agent and not init_all:
        agent, init_all = _select_agent_interactive(support, ui)
        if agent is None and not init_all:
            return  # User cancelled

    # Initialize agents based on selection
    _initialize_agents(support, agent, init_all, ui)

    # Handle script selection and execution
    if not script:
        scripts_dir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "..", "scripts"
        )
        scripts = _load_scripts(scripts_dir)
        script = _select_script_interactive(scripts, ui)

    if script:
        _execute_script(script, ui)


@cli.command()
@click.option("--agent", "-a", required=True, help="Agent to generate context for")
def context(agent: str) -> None:
    """Create unified context file for an agent"""
    # Set agents_dir to the current working directory for installed tools
    agents_dir: str = os.getcwd()

    # If registry not found in current directory, try super_agents subdirectory
    registry_path = os.path.join(agents_dir, "agent_registry.yaml")
    if not os.path.exists(registry_path):
        potential_agent_dir = os.path.join(agents_dir, "super_agents")
        if os.path.exists(potential_agent_dir):
            agents_dir = potential_agent_dir

    support: AgentSupport = AgentSupport(agents_dir)

    if support.create_agent_context_file(agent):
        click.secho(f"✓ Context file created for {agent}", fg="green")
    else:
        click.secho(f"✗ Failed to create context for {agent}", fg="red")
        sys.exit(1)


@cli.command()
def list_agents() -> None:
    """List all super-agents in the system"""
    # Set agents_dir to the current working directory for installed tools
    agents_dir: str = os.getcwd()

    # If registry not found in current directory, try super_agents subdirectory
    registry_path = os.path.join(agents_dir, "agent_registry.yaml")
    if not os.path.exists(registry_path):
        potential_agent_dir = os.path.join(agents_dir, "super_agents")
        if os.path.exists(potential_agent_dir):
            agents_dir = potential_agent_dir

    support: AgentSupport = AgentSupport(agents_dir)
    agent_specs: Dict[str, Dict[str, Any]] = support.load_agent_specs()

    if not agent_specs:
        click.secho("No agent specifications found", fg="yellow")
        return

    print("\n📋 AICODE Labs Super-Agents\n")
    print("=" * 60)

    # Group by division
    divisions: Dict[str, List[tuple]] = {}
    for agent_id, spec in agent_specs.items():
        division = spec.get("division", "Other")
        if division not in divisions:
            divisions[division] = []
        divisions[division].append((agent_id, spec))

    for division in sorted(divisions.keys()):
        click.secho(f"\n{division}", fg="cyan", bold=True)
        click.echo("-" * 60)

        for agent_id, spec in sorted(divisions[division]):
            title = spec.get("title", agent_id)
            mission = spec.get("mission", "")
            capabilities = spec.get("capabilities", [])

            click.echo(f"\n{agent_id} ({title})")
            click.echo(f"  Mission: {mission[:80]}...")
            if capabilities:
                click.echo(f"  Capabilities: {', '.join(capabilities[:3])}")

    print("\n" + "=" * 60 + "\n")


def _format_agent_section(title: str, items: List[str]) -> str:
    """Format a section of the agent information."""
    if not items:
        return ""

    section = f"\n{title}:"
    for item in items:
        section += f"\n  • {item}"
    return section


def _format_agent_info(spec: Dict[str, Any], agent_id: str) -> str:
    """Format comprehensive agent information."""
    output = f"\n{spec.get('title', agent_id)}"
    output += f"\n{'=' * 60}"
    output += f"\n\nID: {agent_id}"
    output += f"\nDivision: {spec.get('division', 'Unknown')}"
    output += f"\n\nMission:\n  {spec.get('mission', 'N/A')}"

    if spec.get("capabilities"):
        output += _format_agent_section("Capabilities", spec.get("capabilities"))

    if spec.get("tools"):
        output += _format_agent_section("Tools", spec.get("tools"))

    if spec.get("inputs"):
        output += _format_agent_section("Accepts", spec.get("inputs"))

    if spec.get("outputs"):
        output += _format_agent_section("Produces", spec.get("outputs"))

    if spec.get("delegates_to"):
        output += _format_agent_section("Delegates To", spec.get("delegates_to"))

    output += f"\n\n{'=' * 60}\n"
    return output


@cli.command()
@click.option("--agent", "-a", required=True, help="Agent to show help for")
def show_agent(agent: str) -> None:
    """Show detailed information about a super-agent"""
    # Set agents_dir to the current working directory for installed tools
    agents_dir: str = os.getcwd()

    # If registry not found in current directory, try super_agents subdirectory
    registry_path = os.path.join(agents_dir, "agent_registry.yaml")
    if not os.path.exists(registry_path):
        potential_agent_dir = os.path.join(agents_dir, "super_agents")
        if os.path.exists(potential_agent_dir):
            agents_dir = potential_agent_dir

    support: AgentSupport = AgentSupport(agents_dir)
    agent_specs: Dict[str, Dict[str, Any]] = support.load_agent_specs()

    if agent not in agent_specs:
        click.secho(f"Agent '{agent}' not found", fg="red")
        sys.exit(1)

    spec: Dict[str, Any] = agent_specs[agent]

    formatted_info = _format_agent_info(spec, agent)
    click.secho(formatted_info, fg="white")


@cli.command()
def status() -> None:
    """Show system status"""
    # Set agents_dir to the current working directory for installed tools
    agents_dir: str = os.getcwd()

    # If registry not found in current directory, try super_agents subdirectory
    registry_path = os.path.join(agents_dir, "agent_registry.yaml")
    if not os.path.exists(registry_path):
        potential_agent_dir = os.path.join(agents_dir, "super_agents")
        if os.path.exists(potential_agent_dir):
            agents_dir = potential_agent_dir

    support: AgentSupport = AgentSupport(agents_dir)

    print("\n📊 System Status\n")
    print("=" * 60)

    # Agent registry status
    registered: List[str] = support.list_registered_agents()
    available: Dict[str, bool] = support.detect_available_agents()
    available_count: int = sum(1 for v in available.values() if v)

    click.echo("\nAgent Support:")
    click.echo(f"  Registered: {len(registered)}")
    click.echo(f"  Available:  {available_count}")

    # Super-agents status
    agent_specs: Dict[str, Dict[str, Any]] = support.load_agent_specs()
    click.echo("\nSuper-Agents:")
    click.echo(f"  Total: {len(agent_specs)}")

    if agent_specs:
        divisions: set = set()
        for spec in agent_specs.values():
            divisions.add(spec.get("division", "Other"))
        click.echo(f"  Divisions: {len(divisions)}")

    print("\n" + "=" * 60 + "\n")


@cli.command()
def check() -> None:
    """Check system prerequisites and configuration"""
    # Set agents_dir to the current working directory for installed tools
    agents_dir: str = os.getcwd()

    # If registry not found in current directory, try super_agents subdirectory
    registry_path = os.path.join(agents_dir, "agent_registry.yaml")
    if not os.path.exists(registry_path):
        potential_agent_dir = os.path.join(agents_dir, "super_agents")
        if os.path.exists(potential_agent_dir):
            agents_dir = potential_agent_dir

    support: AgentSupport = AgentSupport(agents_dir)

    print("\n✓ System Check\n")
    print("=" * 60)

    # Check registry
    try:
        # Access the already loaded registry
        if support.registry:
            click.secho("✓ Agent registry loaded", fg="green")
        else:
            click.secho("✗ Agent registry not loaded", fg="red")
    except Exception as e:
        click.secho(f"✗ Agent registry error: {e}", fg="red")

    # Check agent specs
    try:
        agent_specs: Dict[str, Dict[str, Any]] = support.load_agent_specs()
        click.secho(
            f"✓ Found {len(agent_specs)} super-agent specifications", fg="green"
        )
    except Exception as e:
        click.secho(f"✗ Agent specs error: {e}", fg="red")

    # Check templates
    if os.path.exists(support.templates_dir):
        click.secho("✓ Templates directory exists", fg="green")
    else:
        click.secho(
            "ℹ Templates directory not found (will be created on init)", fg="yellow"
        )

    # Check available agents
    available: Dict[str, bool] = support.detect_available_agents()
    available_count: int = sum(1 for v in available.values() if v)
    if available_count > 0:
        click.secho(f"✓ {available_count} AI agents available", fg="green")
    else:
        click.secho(
            "ℹ No CLI agents detected (IDE-based agents can still be used)",
            fg="yellow",
        )

    print("\n" + "=" * 60 + "\n")


if __name__ == "__main__":
    # Install optional dependencies
    deps_to_install = []

    try:
        from tabulate import tabulate
    except ImportError:
        deps_to_install.append("tabulate")

    try:
        from rich.console import Console  # noqa: F401
    except ImportError:
        deps_to_install.append("rich")

    try:
        import questionary  # noqa: F401
    except ImportError:
        deps_to_install.append("questionary")

    if deps_to_install:
        print("Installing required dependencies...")
        for dep in deps_to_install:
            import subprocess
            import sys

            try:
                # Try pip3 first, then pip as fallback
                result = subprocess.run(
                    [sys.executable, "-m", "pip", "install", dep, "-q"],
                    stderr=subprocess.DEVNULL,
                    check=False,
                )
                if result.returncode != 0:
                    # If the first attempt failed, try again directly with pip module
                    subprocess.run(
                        [sys.executable, "-m", "pip", "install", dep, "-q"],
                        stderr=subprocess.DEVNULL,
                        check=False,
                    )
            except Exception:
                # Log the error but continue with other dependencies
                print(f"Warning: Could not install {dep}")

    cli()
