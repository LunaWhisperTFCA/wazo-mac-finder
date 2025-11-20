"""
Formats and prints script output using the 'rich' library for a better UX.
"""
from typing import Dict
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.theme import Theme

# Define a custom theme for consistent styling
custom_theme = Theme({
    "info": "cyan",
    "warning": "yellow",
    "error": "bold red",
    "success": "bold green",
    "key": "white",
    "value": "bright_cyan",
    "uuid": "dim"
})

# Initialize the console with our theme
console = Console(theme=custom_theme)

def print_device_info(device_data: Dict):
    """
    Displays a rich panel with formatted and enriched device information.
    """
    content = Text()
    
    # --- Basic Device Info ---
    content.append("Tenant ID    : ", style="key")
    content.append(f"{device_data.get('tenant_uuid', 'N/A')}\n", style="uuid")
    content.append("Device Name  : ", style="key")
    content.append(f"{device_data.get('label', 'N/A')}\n", style="value")
    
    # --- Enriched Line Info ---
    line_exten = device_data.get('line_exten', 'Non lié')
    content.append("Line Number  : ", style="key")
    content.append(f"{line_exten}\n", style="value" if line_exten != 'Non lié' else "warning")

    # --- Enriched User Info ---
    user_firstname = device_data.get('user_firstname', '')
    user_lastname = device_data.get('user_lastname', 'Non lié')
    user_fullname = f"{user_firstname} {user_lastname}".strip()
    content.append("User         : ", style="key")
    content.append(f"{user_fullname}\n", style="value" if user_fullname != 'Non lié' else "warning")

    # --- Profile Info ---
    profile_name = device_data.get('profile', {}).get('name', 'N/A') if device_data.get('profile') else 'N/A'
    content.append("Profile      : ", style="key")
    content.append(f"{profile_name}", style="value")

    panel = Panel(
        content,
        title="[success]✅ Appareil trouvé ![/success]",
        border_style="green",
        expand=False
    )
    
    console.print(panel)

def print_not_found(mac_address: str):
    """
    Prints a formatted 'Not Found' message.
    """
    console.print(f"[warning]⚠️  Aucun appareil trouvé avec l'adresse MAC :[/warning] [error]{mac_address}[/error]")

def print_error(message: str):
    """
    Prints a generic, formatted error message.
    """
    console.print(f"[error]❌ ERREUR : {message}[/error]")
