"""MAC address validation and normalization."""
import re
from typing import Optional


class MACValidator:
    """Validator for MAC addresses."""
    
    # Common MAC address formats
    MAC_PATTERNS = [
        r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$',  # XX:XX:XX:XX:XX:XX or XX-XX-XX-XX-XX-XX
        r'^([0-9A-Fa-f]{4}\.){2}([0-9A-Fa-f]{4})$',    # XXXX.XXXX.XXXX
        r'^[0-9A-Fa-f]{12}$',                           # XXXXXXXXXXXX
    ]
    
    @staticmethod
    def validate(mac: str) -> bool:
        """
        Validate if a string is a valid MAC address.
        
        Args:
            mac: MAC address string to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not mac:
            return False
            
        # Remove whitespace
        mac = mac.strip()
        
        # Check against all known patterns
        for pattern in MACValidator.MAC_PATTERNS:
            if re.match(pattern, mac):
                return True
        
        return False
    
    @staticmethod
    def normalize(mac: str, separator: str = ':') -> Optional[str]:
        """
        Normalize MAC address to standard format.
        
        Args:
            mac: MAC address string to normalize
            separator: Separator to use (default: ':')
            
        Returns:
            Normalized MAC address in format XX:XX:XX:XX:XX:XX or None if invalid
        """
        if not MACValidator.validate(mac):
            return None
        
        # Remove all separators and whitespace
        mac_clean = re.sub(r'[.:\-\s]', '', mac).upper()
        
        # Ensure we have exactly 12 hex characters
        if len(mac_clean) != 12:
            return None
        
        # Split into pairs and join with separator
        pairs = [mac_clean[i:i+2] for i in range(0, 12, 2)]
        return separator.join(pairs)
    
    @staticmethod
    def format_for_search(mac: str) -> Optional[str]:
        """
        Format MAC address for Wazo API search.
        
        Args:
            mac: MAC address string
            
        Returns:
            Formatted MAC address for API search or None if invalid
        """
        # Wazo typically uses colon-separated format
        return MACValidator.normalize(mac, separator=':')
