from dataclasses import dataclass
from typing import Any, Dict # Added Dict and Any for the example of creating from a dict

@dataclass(frozen=True) # frozen=True makes instances immutable, similar to not having setters
class Profile:
    """
    Represents a user profile with associated VPN and proxy details,
    as retrieved from the database.
    """
    profile: str
    city: str
    code: str
    timezone: str
    vpn_extra: str
    vpn: str
    password: str
    recovery: str
    browser: str
    proxy_address: str
    proxy_port: int
    proxy_username: str
    proxy_password: str
    authenticator: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Profile':
        """
        Creates a Profile instance from a dictionary (e.g., JSON object).
        """
        # It's important to map the dictionary keys to the class attributes.
        # This assumes the dictionary keys match the attribute names exactly.
        # If there are discrepancies (e.g., 'profile_name' in JSON vs 'profile' in class),
        # you'd need to explicitly map them here.
        return cls(
            profile=data['profile'],
            city=data['city'],
            code=data['code'],
            timezone=data['timezone'],
            vpn_extra=data['vpn_extra'],
            vpn=data['vpn'],
            password=data['password'],
            recovery=data['recovery'],
            browser=data['browser'],
            proxy_address=data['proxy_address'],
            proxy_port=data['proxy_port'],
            proxy_username=data['proxy_username'],
            proxy_password=data['proxy_password'],
            authenticator=data['authenticator']
        )
