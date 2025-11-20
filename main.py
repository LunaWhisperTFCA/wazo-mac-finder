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

def main():
    default_host = os.getenv('WAZO_HOST')
    default_token = os.getenv('WAZO_TOKEN')

    parser = argparse.ArgumentParser(description="Wazo MAC Finder")
    parser.add_argument('-m', '--mac', required=True, help="Adresse MAC à rechercher")
    parser.add_argument('--host', default=default_host, help="Hôte Wazo")
    parser.add_argument('--token', default=default_token, help="Token d'authentification Wazo")
    parser.add_argument('--insecure', action='store_true', help="Désactiver la vérification SSL")
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose logging.')
    
    args = parser.parse_args()
    if args.verbose: setup_logging(args.verbose)

    if not (args.host and args.token):
        print_error("Configuration manquante.")
        sys.exit(1)
    if not MACValidator.validate(args.mac):
        print_error(f"Format d'adresse MAC invalide: {args.mac}")
        sys.exit(1)

    try:
        if not args.verbose: logging.disable(logging.CRITICAL)

        client = WazoClient(host=args.host, token=args.token, insecure=args.insecure)
        device = client.get_rich_device_details(args.mac)

        if not device:
            print_not_found(args.mac)
            sys.exit(2)

        if not device.get('line_exten'):
            console.print(f"[warning]L'appareil [cyan]{device.get('label', args.mac)}[/cyan] n'est lié à aucune ligne.[/warning]")
            
            target_line_id = get_line_id_for_exten(client, '1000')
            device_id = device.get('id')

            if not (target_line_id and device_id):
                print_error("Impossible de trouver l'ID de la ligne 1000 ou l'ID de l'appareil.")
                sys.exit(1)
            
            try:
                choice = input(f"Voulez-vous forcer la liaison Line:{target_line_id} -> Device:{device_id} ? (O/N) ")
                if choice.lower() == 'o':
                    client.force_line_device_link(target_line_id, device_id)
                    console.print("[success]Liaison effectuée. Re-vérification dans 2 secondes...[/success]\n")
                    
                    time.sleep(2)
                    
                    device = client.get_rich_device_details(args.mac)
                    if not device:
                         print_error("Échec de la re-vérification après la liaison.")
                         sys.exit(1)
                else:
                    console.print("Opération annulée.", style="info")
                    sys.exit(0)
            except (EOFError, KeyboardInterrupt):
                console.print("\nOpération annulée.", style="info")
                sys.exit(1)

        print_device_info(device)

    except WazoAPIError as e:
        print_error(f"Erreur API: {e}")
        sys.exit(1)
    except Exception as e:
        print_error(f"Une erreur inattendue est survenue: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()