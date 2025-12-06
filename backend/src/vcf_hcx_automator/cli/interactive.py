from typing import List, Dict, Any, Tuple, Optional
from rich.prompt import Prompt, Confirm
from rich.console import Console
from .formatting import OutputFormatter

class InteractiveResolver:
    """Interactive resolution for ambiguous matches and user input."""

    def __init__(self, formatter: OutputFormatter):
        self.formatter = formatter
        self.console = Console()

    def prompt_for_resolution(self, ambiguous_matches: List[Tuple[str, List[Any]]]) -> Dict[str, str]:
        """Prompt user to resolve ambiguous name matches."""
        resolutions = {}
        for name, matches in ambiguous_matches:
            self.formatter.display_info(f"Ambiguous match for '{name}':")
            choices = []
            for i, match in enumerate(matches):
                # Assuming match is a dictionary or object with a name or id
                match_str = str(match)
                if hasattr(match, 'name'):
                    match_str = f"{match.name} ({getattr(match, 'id', 'No ID')})"
                elif isinstance(match, dict):
                    match_str = f"{match.get('name', 'Unknown')} ({match.get('id', 'No ID')})"
                
                choices.append(f"{i + 1}. {match_str}")
            
            choices.append(f"{len(matches) + 1}. Skip")
            
            self.console.print("\n".join(choices))
            
            choice = Prompt.ask(
                "Select the correct resource",
                choices=[str(i + 1) for i in range(len(matches) + 1)],
                default=str(len(matches) + 1)
            )
            
            choice_idx = int(choice) - 1
            if choice_idx < len(matches):
                selected = matches[choice_idx]
                # Extract ID if possible
                if hasattr(selected, 'id'):
                    resolutions[name] = selected.id
                elif isinstance(selected, dict) and 'id' in selected:
                    resolutions[name] = selected['id']
                else:
                    resolutions[name] = str(selected)
            else:
                self.console.print(f"[yellow]Skipping resolution for {name}[/yellow]")
        
        return resolutions

    def confirm_action(self, message: str, default: bool = False) -> bool:
        """Get user confirmation for an action."""
        return Confirm.ask(message, default=default)

    def prompt_for_input(self, message: str, default: Optional[str] = None, password: bool = False) -> str:
        """Prompt user for input."""
        return Prompt.ask(message, default=default, password=password)

    def prompt_for_credentials(self, system: str) -> Tuple[str, str]:
        """Securely prompt for system credentials."""
        self.formatter.display_info(f"Enter credentials for {system}")
        username = Prompt.ask("Username")
        password = Prompt.ask("Password", password=True)
        return username, password
