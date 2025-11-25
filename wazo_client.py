"""
Wazo API client with added methods for deleting test data.
"""
import logging
from typing import Dict, Optional
import requests
import urllib3

from response_formatter import console

# Suppress InsecureRequestWarning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class WazoAPIError(Exception):
    pass

class WazoClient:
    # ... (existing __init__, _make_request, and GET methods remain the same)
    
    def __init__(self, host: str, token: str, insecure: bool = False, timeout: int = 30):
        self.base_url = host.rstrip('/')
        self.insecure = insecure
        self.timeout = timeout
        self.logger = logging.getLogger(__name__)
        self.headers = {'X-Auth-Token': token, 'Content-Type': 'application/json', 'Accept': 'application/json'}

    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict:
        url = f"{self.base_url}{endpoint}"
        self.logger.debug(f"Making {method} request to {url}")
        try:
            response = requests.request(method=method, url=url, headers=self.headers, verify=not self.insecure, timeout=self.timeout, **kwargs)
            response.raise_for_status()
            # For DELETE requests, a 204 No Content is a success
            if response.status_code == 204:
                return {"status": "success"}
            return response.json() if response.content else {}
        except requests.exceptions.HTTPError as err:
            raise WazoAPIError(f"HTTP Error: {err}")
        except requests.exceptions.RequestException as e:
            raise WazoAPIError(f"Request Error: {e}")

    # --- GET methods from before ---
    def get_device_by_mac(self, mac: str) -> Optional[Dict]:
        self.logger.info(f"Searching for device with MAC: {mac}")
        response = self._make_request('GET', '/api/confd/1.1/devices', params={'search': mac})
        return response.get('items', [{}])[0] if response.get('total', 0) > 0 else None

    def get_complete_device_details(self, device_id: str) -> Optional[Dict]:
        if not device_id: return None
        self.logger.info(f"Fetching complete details for device ID: {device_id}")
        return self._make_request('GET', f'/api/confd/1.1/devices/{device_id}')

    def find_line_by_device_id(self, device_id: str) -> Optional[Dict]:
        if not device_id: return None
        all_lines = self._make_request('GET', '/api/confd/1.1/lines').get('items', [])
        for line in all_lines:
            if line.get('device_id') == device_id:
                return line
        return None

    def find_user_by_line_id(self, line_id: int) -> Optional[Dict]:
        if not line_id: return None
        users = self._make_request('GET', '/api/confd/1.1/users').get('items', [])
        for user in users:
            if any(l.get('id') == line_id for l in user.get('lines', [])):
                return user
        return None
    
    # --- Link/Unlink method ---
    def force_line_device_link(self, line_id: int, device_id: str):
        self.logger.info(f"Attempting to link Line {line_id} with Device {device_id}...")
        endpoint = f'/api/confd/1.1/lines/{line_id}/devices/{device_id}'
        self._make_request('PUT', endpoint)

    # --- DELETION METHODS FOR CLEANUP ---
    def dissociate_device_from_line(self, line_id: int, device_id: str):
        """Dissociates a device from a line."""
        self.logger.info(f"Dissociating Device {device_id} from Line {line_id}...")
        endpoint = f'/api/confd/1.1/lines/{line_id}/devices/{device_id}'
        self._make_request('DELETE', endpoint)
        
    def delete_device(self, device_id: str):
        """Deletes a device."""
        self.logger.info(f"Deleting Device {device_id}...")
        endpoint = f'/api/confd/1.1/devices/{device_id}'
        self._make_request('DELETE', endpoint)

    def delete_line(self, line_id: int):
        """Deletes a line."""
        self.logger.info(f"Deleting Line {line_id}...")
        endpoint = f'/api/confd/1.1/lines/{line_id}'
        self._make_request('DELETE', endpoint)

    def delete_user(self, user_uuid: str):
        """Deletes a user."""
        self.logger.info(f"Deleting User {user_uuid}...")
        endpoint = f'/api/confd/1.1/users/{user_uuid}'
        self._make_request('DELETE', endpoint)

    # --- Orchestrator method ---
    def get_rich_device_details(self, mac: str) -> Optional[Dict]:
        # ... (logic remains the same)
        device = self.get_device_by_mac(mac)
        if not device: return None
        device_id = device.get('id')
        if not device_id: return device
        device_details = self.get_complete_device_details(device_id)
        if device_details:
            device['label'] = device_details.get('label', 'N/A')
            profile_info = "N/A"
            if device_details.get('template_id'):
                profile_info = f"Template ID: {device_details['template_id']}"
            elif device_details.get('model'):
                profile_info = f"Model: {device_details.get('model')}"
            device['profile'] = {'name': profile_info}
        line_details = self.find_line_by_device_id(device_id)
        if not line_details:
            self.logger.warning(f"No line found associated with device {device_id}.")
            return device
        line_id = line_details.get('id')
        user_details = self.find_user_by_line_id(line_id)
        if line_details.get('extensions'):
            device['line_exten'] = line_details['extensions'][0].get('exten')
        if user_details:
            device['user_firstname'] = user_details.get('firstname')
            device['user_lastname'] = user_details.get('lastname')
        return device