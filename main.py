import os
import sys
import time
import argparse
import logging
from pathlib import Path
from dotenv import load_dotenv

# --- BLOC DE CHARGEMENT .ENV ROBUSTE ---
BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = BASE_DIR / '.env'
if ENV_PATH.exists():
    load_dotenv(dotenv_path=ENV_PATH, override=True)
# --- FIN DU BLOC ---

from mac_validator import MACValidator
from wazo_client import WazoClient, WazoAPIError
from response_formatter import console, print_device_info, print_not_found, print_error
from config import Config

def setup_logging(verbose: bool = False):
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=level, format='%(asctime)s - %(levelname)s - %(message)s')

def get_line_id_for_exten(client: WazoClient, exten: str) -> str | None:
    all_lines = client._make_request('GET', '/api/confd/1.1/lines').get('items', [])
    for line in all_lines:
        if line.get('extensions'):
            for extension in line['extensions']:
                if extension.get('exten') == exten:
                    return line.get('id')
    return None

def process_device_on_server(client: WazoClient, mac: str, server_name: str) -> bool:
    """
    Process device on a specific server. Returns True if device found and processed, False otherwise.
    """
    try:
        console.rule(f"[bold blue]Scanning {server_name}[/bold blue]")
        device = client.get_rich_device_details(mac)

        if not device:
            console.print(f"[dim]Device not found on {server_name}[/dim]")
            return False

        if not device.get('line_exten'):
            console.print(f"[warning]L'appareil [cyan]{device.get('label', mac)}[/cyan] n'est lié à aucune ligne sur {server_name}.[/warning]")
            
            target_line_id = get_line_id_for_exten(client, '1000')
            device_id = device.get('id')

            if not (target_line_id and device_id):
                print_error(f"Impossible de trouver l'ID de la ligne 1000 ou l'ID de l'appareil sur {server_name}.")
                return True # Device found but error in processing, stop scanning other servers
            
            try:
                choice = input(f"Voulez-vous forcer la liaison Line:{target_line_id} -> Device:{device_id} sur {server_name} ? (O/N) ")
                if choice.lower() == 'o':
                    client.force_line_device_link(target_line_id, device_id)
                    console.print("[success]Liaison effectuée. Re-vérification dans 2 secondes...[/success]\n")
                    
                    time.sleep(2)
                    
                    device = client.get_rich_device_details(mac)
                    if not device:
                         print_error("Échec de la re-vérification après la liaison.")
                         return True
                else:
                    console.print("Opération annulée.", style="info")
                    return True
            except (EOFError, KeyboardInterrupt):
                console.print("\nOpération annulée.", style="info")
                sys.exit(1)

        console.rule("[bold green]Result[/bold green]")
        print_device_info(device)
        return True

    except WazoAPIError as e:
        console.print(f"[error]Error on {server_name}: {e}[/error]")
        return False
    except Exception as e:
        console.print(f"[error]Unexpected error on {server_name}: {e}[/error]")
        return False

def main():
    config = Config()
    
    parser = argparse.ArgumentParser(description="Wazo MAC Finder")
    parser.add_argument('-m', '--mac', required=True, help="Adresse MAC à rechercher")
    parser.add_argument('--host', help="Hôte Wazo (Override)")
    parser.add_argument('--token', help="Token d'authentification Wazo (Override)")
    parser.add_argument('--server', type=int, help="Numéro du serveur à scanner (ex: 2 pour WAZO_HOST2)")
    parser.add_argument('--insecure', action='store_true', help="Désactiver la vérification SSL")
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose logging.')
    
    args = parser.parse_args()
    if args.verbose: setup_logging(args.verbose)
    if not args.verbose: logging.disable(logging.CRITICAL)

    if not MACValidator.validate(args.mac):
        print_error(f"Format d'adresse MAC invalide: {args.mac}")
        sys.exit(1)

    # Determine which servers to scan
    servers_to_scan = []

    # Case 1: Manual Override
    if args.host and args.token:
        servers_to_scan.append({'host': args.host, 'token': args.token, 'name': 'Manual Override Server'})
    
    # Case 2: Specific Server Selection
    elif args.server:
        # Adjust for 1-based index
        index = args.server - 1
        if 0 <= index < len(config.servers):
            servers_to_scan.append(config.servers[index])
        else:
            print_error(f"Serveur numéro {args.server} non trouvé dans la configuration.")
            sys.exit(1)
            
    # Case 3: Default - Scan all configured servers
    else:
        servers_to_scan = config.servers

    if not servers_to_scan:
        print_error("Aucune configuration de serveur trouvée. Vérifiez votre fichier .env.")
        sys.exit(1)

    found_any = False
    for server_conf in servers_to_scan:
        client = WazoClient(host=server_conf['host'], token=server_conf['token'], insecure=args.insecure)
        if process_device_on_server(client, args.mac, server_conf['name']):
            found_any = True
            break # Stop scanning if found

    if not found_any:
        console.rule("[bold red]Result[/bold red]")
        print_not_found(args.mac)
        sys.exit(2)

if __name__ == '__main__':
    main()