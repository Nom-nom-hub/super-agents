"""
Beautiful interactive CLI UI for Super-Agents initialization
Uses Rich library for beautiful terminal output and custom interactive selection
"""

import sys

from rich.align import Align
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.text import Text

console = Console()

LOGO = r"""
    ███████╗██╗   ██╗██████╗ ███████╗██████╗     █████╗  ██████╗ ███████╗███╗   ██╗████████╗███████╗
    ██╔════╝██║   ██║██╔══██╗██╔════╝██╔══██╗   ██╔══██╗██╔════╝ ██╔════╝████╗  ██║╚══██╔══╝██╔════╝
    ███████╗██║   ██║██████╔╝█████╗  ██████╔╝   ███████║██║  ███╗█████╗  ██╔██╗ ██║   ██║   █████╗
    ╚════██║██║   ██║██╔═══╝ ██╔══╝  ██╔══██╗   ██╔══██║██║   ██║██╔══╝  ██║╚██╗██║   ██║   ██╔══╝
    ███████║╚██████╔╝██║     ███████╗██║  ██║   ██║  ██║╚██████╔╝███████╗██║ ╚████║   ██║   ███████╗
    ╚══════╝ ╚═════╝ ╚═╝     ╚══════╝╚═╝  ╚═╝   ╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚═╝  ╚═══╝   ╚═╝   ╚══════╝
"""


class SuperAgentsUI:
    """Beautiful interactive CLI for Super-Agents"""

    def __init__(self):
        self.console = console

    def show_header(self):
        """Display the beautiful header with logo"""
        self.console.clear()
        # Logo
        logo_text = Text(LOGO, style="bold cyan")
        self.console.print(logo_text)

        # Subtitle
        subtitle = Text("AICODE Labs - AI Agent Initialization", justify="center")
        subtitle.stylize("bold magenta", 0, len(subtitle))
        self.console.print(Align.center(subtitle))
        self.console.print()

    def select_agent(self, agents_dict):
        """
        Interactive agent selection with arrow keys

        Args:
            agents_dict: Dict of {agent_id: agent_config}

        Returns:
            Selected agent ID or "all" or None (cancelled)
        """
        self.show_header()

        # Create menu items
        menu_items = []
        for agent_id, config in agents_dict.items():
            menu_items.append(("agent", agent_id, config["name"]))
        menu_items.append(("action", "all", "Initialize All Agents"))

        return self._show_menu(
            title="Select an Agent",
            items=menu_items,
            color_map={"agent": "green", "action": "yellow"},
        )

    def select_script(self, scripts_dict):
        """
        Interactive script selection with arrow keys

        Args:
            scripts_dict: Dict of {script_name: script_path}

        Returns:
            Selected script name or None
        """
        self.console.print()

        menu_items = [("skip", None, "Skip")]
        for script_name in sorted(scripts_dict.keys()):
            menu_items.append(("script", script_name, script_name))

        return self._show_menu(
            title="Run a Script (Optional)",
            items=menu_items,
            color_map={"script": "cyan", "skip": "gray50"},
        )

    def _display_menu_items(self, items, current_selection, color_map):
        """Display the menu items with proper highlighting."""
        for idx, (item_type, _value, display_name) in enumerate(items):
            color = color_map.get(item_type, "white")

            if idx == current_selection:
                # Selected item
                line = Text(f"  ❯ {display_name}", style=f"bold {color} on blue")
            else:
                # Unselected item
                line = Text(f"    {display_name}", style=color)

            self.console.print(line)

    def _handle_key_input(self, current_selection, items):
        """Handle keyboard input and return new selection or value."""
        import sys

        key = sys.stdin.read(1)

        if ord(key) == 27:  # ESC
            sys.stdin.read(2)  # Read [ and arrow direction
            arrow = sys.stdin.read(1)

            if arrow == "A":  # Up arrow
                return (current_selection - 1) % len(items)
            elif arrow == "B":  # Down arrow
                return (current_selection + 1) % len(items)
        elif ord(key) == 13:  # Enter
            _, value, _ = items[current_selection]
            return value
        elif ord(key) == 3:  # Ctrl+C
            self.console.print()
            self.console.print(Text("⊘ Cancelled", style="bold red"))
            return None

        return current_selection  # No change if key not recognized

    def _show_menu(self, title, items, color_map=None):
        """
        Display an interactive menu with arrow key selection

        Args:
            title: Menu title
            items: List of (item_type, value, display_name)
            color_map: Dict mapping item_type to color

        Returns:
            Selected value or None (cancelled)
        """
        if color_map is None:
            color_map = {}

        current_selection = 0

        while True:
            self.console.clear()
            self.show_header()

            # Title
            title_text = Text(title, style="bold cyan")
            self.console.print(Align.left(title_text))
            self.console.print()

            # Menu items
            self._display_menu_items(items, current_selection, color_map)

            self.console.print()
            self.console.print(
                Text(
                    "  Use ↑/↓ to navigate, Enter to select, Ctrl+C to cancel",
                    style="dim",
                )
            )

            # Get user input
            # Check platform first without try-except to avoid the termios import error
            if sys.platform == "win32":
                # Windows doesn't support arrow keys easily
                return self._fallback_menu(items)

            try:
                # Unix/Mac: read arrow keys
                import termios
                import tty

                fd = sys.stdin.fileno()
                old_settings = termios.tcgetattr(fd)

                try:
                    tty.setraw(fd)

                    result = self._handle_key_input(current_selection, items)

                    # If result is None (cancelled) or a value (selected), return it
                    if result is None or not isinstance(result, int):
                        return result
                    else:
                        current_selection = result  # Update selection

                finally:
                    termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

            except ImportError:
                # Fallback for systems without tty support
                return self._fallback_menu(items)
            except (OSError, termios.error):
                # Fallback for systems where termios doesn't work properly
                return self._fallback_menu(items)

    def _fallback_menu(self, items):
        """Fallback to numbered menu when arrow keys not available"""
        self.console.clear()
        self.show_header()

        self.console.print(Text("Available Options:", style="bold cyan"))
        self.console.print()

        for idx, (_item_type, _value, display_name) in enumerate(items, 1):
            self.console.print(f"  {idx}. {display_name}")

        self.console.print("  0. Cancel")
        self.console.print()

        choice = Prompt.ask("Select an option", default="0")

        try:
            choice_num = int(choice)
            if choice_num == 0:
                self.console.print(Text("⊘ Cancelled", style="bold red"))
                return None
            elif 1 <= choice_num <= len(items):
                _, value, _ = items[choice_num - 1]
                return value
            else:
                self.console.print(Text("Invalid choice", style="bold red"))
                return None
        except ValueError:
            self.console.print(Text("Invalid input", style="bold red"))
            return None

    def show_progress(self, message, completed=False):
        """Show progress message"""
        if completed:
            self.console.print(Text(f"✓ {message}", style="bold green"))
        else:
            self.console.print(Text(f"⟳ {message}...", style="bold cyan"))

    def show_success(self, message):
        """Show success message"""
        self.console.print()
        panel = Panel(
            Text(f"✓ {message}", justify="center", style="bold green"),
            style="green",
            padding=(1, 2),
        )
        self.console.print(panel)
        self.console.print()

    def show_error(self, message):
        """Show error message"""
        self.console.print()
        panel = Panel(
            Text(f"✗ {message}", justify="center", style="bold red"),
            style="red",
            padding=(1, 2),
        )
        self.console.print(panel)
        self.console.print()

    def show_info(self, message):
        """Show info message"""
        self.console.print(Text(f"ℹ {message}", style="bold cyan"))
