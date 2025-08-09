from dataclasses import dataclass
from typing import Any, Dict # Added Dict and Any for the example of creating from a dict

@dataclass(frozen=False) # frozen=True makes instances immutable, similar to not having setters
class Profile:
    """
    Represents a user profile with associated VPN and proxy details,
    as retrieved from the database.
    """
    profile: str
    code: str
    password: str
    recovery: str
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
            code=data['code'],
            password=data['password'],
            recovery=data['recovery'],
            authenticator=data['authenticator']
        )
