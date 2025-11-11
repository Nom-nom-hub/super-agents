#!/usr/bin/env python3
"""
AICODE Labs - Super-Agents CLI

Command-line interface for initializing and managing multi-agent support.
Inspired by GitHub Spec Kit's Specify CLI.
"""

import os
import sys

try:
    import click
except ImportError:
    print("Error: 'click' is required. Install with: pip3 install click")
    sys.exit(1)

try:
    from tabulate import tabulate
except ImportError:
    # Fallback if tabulate not available
    def tabulate(data, headers=None, tablefmt=None):
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
    from .agent_support import AgentSupport
except ImportError:
    # For development/standalone execution
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from agent_support import AgentSupport

# Import custom UI if rich is available
if HAS_RICH:
    try:
        from .ui import SuperAgentsUI
    except ImportError:
        # For development/standalone execution
        import sys
        import os
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from ui import SuperAgentsUI


@click.group()
def cli():
    """AICODE Labs Super-Agents CLI"""
    pass


@cli.command()
def detect():
    """Detect available AI agents on system"""
    # Set company_dir to the directory where this module is located
    company_dir = os.path.dirname(os.path.abspath(__file__))
    support = AgentSupport(company_dir)
    available = support.detect_available_agents()

    print("\n📊 AI Agent Detection Report\n")
    print("=" * 60)

    data = []
    for agent_id, config in sorted(support.registry.get("agents", {}).items()):
        status = "✓ Available" if available.get(agent_id) else "✗ Not Found"
        cli_tool = config.get("cli_tool", "IDE-based")
        data.append([agent_id, config["name"], cli_tool, status])

    headers = ["Agent ID", "Name", "CLI Tool / Type", "Status"]
    print(tabulate(data, headers=headers, tablefmt="grid"))

    available_agents = [a for a, v in available.items() if v]
    print(f"\n✓ Found {len(available_agents)} available agents")

    if available_agents:
        print(f"\nAvailable: {', '.join(available_agents)}\n")
    else:
        print("\nℹ️  No CLI agents detected. Install agents or use IDE-based ones.\n")


def _load_scripts(scripts_dir):
    """Load available scripts from scripts directory"""
    scripts = {}
    if os.path.exists(scripts_dir):
        for filename in os.listdir(scripts_dir):
            if filename.endswith(('.sh', '.ps1')):
                name = filename.rsplit('.', 1)[0]
                scripts[name] = os.path.join(scripts_dir, filename)
    return scripts


@cli.command()
@click.option(
    "--agent",
    "-a",
    help="Specific agent to initialize (claude, copilot, amp, gemini, cursor, etc.)",
)
@click.option("--all", "init_all", is_flag=True, help="Initialize for all available agents")
@click.option("--script", "-s", help="Run a script after initialization")
@click.option("--project", "-p", help="Project context to use for initialization")
def init(agent, init_all, script, project):
    """Initialize super-agents for AI agents with comprehensive context files"""
    # Set company_dir to the directory where this module is located
    company_dir = os.path.dirname(os.path.abspath(__file__))
    support = AgentSupport(company_dir)
    ui = SuperAgentsUI() if HAS_RICH else None

    if not agent and not init_all:
        # Interactive mode - select agent
        registered = support.list_registered_agents()
        agents_dict = {}
        
        for agent_id in registered:
            config = support.get_agent_config(agent_id)
            agents_dict[agent_id] = config
        
        if ui:
            # Use beautiful custom UI
            selection = ui.select_agent(agents_dict)
            if selection is None:
                return
            elif selection == "all":
                init_all = True
            else:
                agent = selection
        else:
            # Fallback to click prompts
            click.echo("\n🤖  Super-Agents Initialization\n")
            click.echo("Select an agent:")
            agent_list = list(registered)
            for i, a in enumerate(agent_list, 1):
                config = support.get_agent_config(a)
                click.echo(f"  {i}. {a} ({config['name']})")
            click.echo(f"  {len(agent_list) + 1}. All agents")
            click.echo(f"  0. Cancel\n")
            
            choice = click.prompt("Enter your choice", type=int)
            
            if choice == 0:
                return
            elif choice == len(agent_list) + 1:
                init_all = True
            elif 1 <= choice <= len(agent_list):
                agent = agent_list[choice - 1]
            else:
                click.secho("Invalid choice", fg="red")
                return

    if init_all:
        if ui:
            ui.show_progress("Initializing all agents")
        else:
            click.echo("\nInitializing all agents...")
        
        count = support.initialize_for_all_available()
        
        if ui:
            ui.show_success(f"Initialized {count} agents successfully!")
        else:
            click.secho(f"\n✓ Initialized {count} agents successfully!", fg="green", bold=True)
    elif agent:
        if ui:
            ui.show_progress(f"Initializing {agent}")
        else:
            click.echo(f"\nInitializing {agent}...")
        
        success = support.initialize_for_agent(agent)
        
        if success:
            if ui:
                ui.show_success(f"Initialized {agent} successfully!")
            else:
                click.secho(f"\n✓ Initialized {agent} successfully!", fg="green", bold=True)
        else:
            if ui:
                ui.show_error(f"Failed to initialize {agent}")
            else:
                click.secho(f"\n✗ Failed to initialize {agent}", fg="red", bold=True)
            sys.exit(1)
    
    # Interactive script selection if not specified
    if not script:
        scripts_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts')
        scripts = _load_scripts(scripts_dir)
        
        if scripts:
            if ui:
                script = ui.select_script(scripts)
            else:
                click.echo("\nAvailable scripts:")
                script_list = sorted(scripts.keys())
                for i, script_name in enumerate(script_list, 1):
                    click.echo(f"  {i}. {script_name}")
                click.echo(f"  0. Skip\n")
                
                script_choice = click.prompt("Select a script", type=int, default=0)
                
                if 1 <= script_choice <= len(script_list):
                    script = script_list[script_choice - 1]
    
    # Execute script if selected
    if script:
        scripts_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts')
        scripts = _load_scripts(scripts_dir)
        
        if script in scripts:
            script_path = scripts[script]
            
            if ui:
                ui.show_progress(f"Running {script}")
            else:
                click.echo(f"\nRunning {script}...")
            
            result = os.system(f"bash {script_path}" if script.endswith('.sh') else f"powershell -File {script_path}")
            
            if result == 0:
                if ui:
                    ui.show_success(f"Script executed successfully")
                else:
                    click.secho(f"\n✓ Script executed successfully", fg="green", bold=True)
            else:
                if ui:
                    ui.show_error(f"Script execution failed")
                else:
                    click.secho(f"\n✗ Script execution failed", fg="red", bold=True)
        else:
            if ui:
                ui.show_error(f"Script '{script}' not found")
            else:
                click.secho(f"✗ Script '{script}' not found", fg="red")


@cli.command()
@click.option(
    "--agent", "-a", required=True, help="Agent to generate context for"
)
def context(agent):
    """Create unified context file for an agent"""
    # Set company_dir to the directory where this module is located
    company_dir = os.path.dirname(os.path.abspath(__file__))
    support = AgentSupport(company_dir)

    if support.create_agent_context_file(agent):
        click.secho(f"✓ Context file created for {agent}", fg="green")
    else:
        click.secho(f"✗ Failed to create context for {agent}", fg="red")
        sys.exit(1)


@cli.command()
def list_agents():
    """List all super-agents in the system"""
    # Set company_dir to the directory where this module is located
    company_dir = os.path.dirname(os.path.abspath(__file__))
    support = AgentSupport(company_dir)
    agent_specs = support.load_agent_specs()

    if not agent_specs:
        click.secho("No agent specifications found", fg="yellow")
        return

    print("\n📋 AICODE Labs Super-Agents\n")
    print("=" * 60)

    # Group by division
    divisions = {}
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


@cli.command()
@click.option("--agent", "-a", required=True, help="Agent to show help for")
def show_agent(agent):
    """Show detailed information about a super-agent"""
    # Set company_dir to the directory where this module is located
    company_dir = os.path.dirname(os.path.abspath(__file__))
    support = AgentSupport(company_dir)
    agent_specs = support.load_agent_specs()

    if agent not in agent_specs:
        click.secho(f"Agent '{agent}' not found", fg="red")
        sys.exit(1)

    spec = agent_specs[agent]

    click.secho(f"\n{spec.get('title', agent)}", fg="cyan", bold=True)
    click.echo("=" * 60)

    click.echo(f"\nID: {agent}")
    click.echo(f"Division: {spec.get('division', 'Unknown')}")
    click.echo(f"\nMission:")
    click.echo(f"  {spec.get('mission', 'N/A')}")

    if spec.get("capabilities"):
        click.echo(f"\nCapabilities:")
        for cap in spec.get("capabilities"):
            click.echo(f"  • {cap}")

    if spec.get("tools"):
        click.echo(f"\nTools:")
        for tool in spec.get("tools"):
            click.echo(f"  • {tool}")

    if spec.get("inputs"):
        click.echo(f"\nAccepts:")
        for input_type in spec.get("inputs"):
            click.echo(f"  • {input_type}")

    if spec.get("outputs"):
        click.echo(f"\nProduces:")
        for output_type in spec.get("outputs"):
            click.echo(f"  • {output_type}")

    if spec.get("delegates_to"):
        click.echo(f"\nDelegates To:")
        for delegate in spec.get("delegates_to"):
            click.echo(f"  • {delegate}")

    click.echo("\n" + "=" * 60 + "\n")


@cli.command()
def status():
    """Show system status"""
    # Set company_dir to the directory where this module is located
    company_dir = os.path.dirname(os.path.abspath(__file__))
    support = AgentSupport(company_dir)

    print("\n📊 System Status\n")
    print("=" * 60)

    # Agent registry status
    registered = support.list_registered_agents()
    available = support.detect_available_agents()
    available_count = sum(1 for v in available.values() if v)

    click.echo(f"\nAgent Support:")
    click.echo(f"  Registered: {len(registered)}")
    click.echo(f"  Available:  {available_count}")

    # Super-agents status
    agent_specs = support.load_agent_specs()
    click.echo(f"\nSuper-Agents:")
    click.echo(f"  Total: {len(agent_specs)}")

    if agent_specs:
        divisions = set()
        for spec in agent_specs.values():
            divisions.add(spec.get("division", "Other"))
        click.echo(f"  Divisions: {len(divisions)}")

    print("\n" + "=" * 60 + "\n")


@cli.command()
def check():
    """Check system prerequisites and configuration"""
    # Set company_dir to the directory where this module is located
    company_dir = os.path.dirname(os.path.abspath(__file__))
    support = AgentSupport(company_dir)

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
        agent_specs = support.load_agent_specs()
        click.secho(f"✓ Found {len(agent_specs)} super-agent specifications", fg="green")
    except Exception as e:
        click.secho(f"✗ Agent specs error: {e}", fg="red")

    # Check templates
    if os.path.exists(support.templates_dir):
        click.secho(f"✓ Templates directory exists", fg="green")
    else:
        click.secho(f"ℹ Templates directory not found (will be created on init)", fg="yellow")

    # Check available agents
    available = support.detect_available_agents()
    available_count = sum(1 for v in available.values() if v)
    if available_count > 0:
        click.secho(f"✓ {available_count} AI agents available", fg="green")
    else:
        click.secho(f"ℹ No CLI agents detected (IDE-based agents can still be used)", fg="yellow")

    print("\n" + "=" * 60 + "\n")


if __name__ == "__main__":
    # Install optional dependencies
    deps_to_install = []
    
    try:
        from tabulate import tabulate
    except ImportError:
        deps_to_install.append("tabulate")
    
    try:
        from rich.console import Console
    except ImportError:
        deps_to_install.append("rich")
    
    try:
        import questionary
    except ImportError:
        deps_to_install.append("questionary")
    
    if deps_to_install:
        print("Installing required dependencies...")
        for dep in deps_to_install:
            os.system(f"pip3 install {dep} -q 2>/dev/null || pip install {dep} -q")

    cli()
