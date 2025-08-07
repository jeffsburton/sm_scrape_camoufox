# utils/web.py
import json
import os
import time
from enum import Enum
from pathlib import PurePosixPath
from profile import Profile
from typing import Any, Dict, List

import requests                       # pip install requests

BASE_URL = "https://smg.c2r.one/"

def set_current_task() -> None:
    """
    Stub – replace with your real tracker.
    """
    pass

def json_web_call(
    url_fragment: str,
    body: Dict[str, Any],
    *,
    tries: int = 10,
    timeout: int = 15,                # seconds for the HTTP request itself
) -> Dict[str, Any]:
    """
    POST a JSON body to `https://smg.c2r.one/<url_fragment>` and
    return the parsed JSON response.

    • Retries network faults up to `tries` times (2‑second delay).
    • Raises RuntimeError on non‑2xx HTTP status codes.
    • Raises the underlying exception on final network failure.
    """
    set_current_task()

    # normalise slashes (so “foo/bar” -> “…/foo/bar”)
    full_url = BASE_URL + str(PurePosixPath(url_fragment))

    resp = None

    last_exc: Exception | None = None
    for attempt in range(tries):
        try:
            resp = requests.post(
                full_url,
                json=body,                        # requests dumps to JSON + sets header
                headers={"Content-Type": "application/json"},
                timeout=timeout,
            )
            break                                # success → exit retry‑loop
        except requests.RequestException as exc:
            last_exc = exc
            if attempt == tries - 1:
                raise                           # out of retries → propagate
            time.sleep(2)

    # HTTP status‑code handling
    if not resp.ok:
        raise RuntimeError(
            f"HTTP error for json call {url_fragment}: "
            f"{resp.status_code}, payload: {resp.text}"
        )

    # Parse JSON explicitly so we can give a better error message
    try:
        return resp.json()
    except json.JSONDecodeError as exc:
        print(f"Error parsing JSON from {url_fragment!r}: {resp.text}", flush=True)
        raise

# Define the Enum for account status slugs
class AccountStatus(Enum):
    FRAGILE = "fragile"
    INACTIVE = "inactive"
    NOT_SETUP = "not setup"
    OTHER_PROBLEM = "other_problem"
    READY = "ready"
    SUSPENDED = "suspended"
    THAWING = "thawing"
    WARMING = "warming"



def get_accounts(status: AccountStatus) -> List[Profile]: # Changed return type to List[Profile]
    # The json_web_call is expected to return a list of dictionaries,
    # each representing a profile.
    accounts_data = json_web_call(
        "accounts.php", # Keep "accounts.php" as discussed previously
        {
            "computer": os.environ['COMPUTERNAME'],
            "platform_id": 1,
            "status": status.value
        },
    )

    # Convert each dictionary into a Profile object
    profile_objects = [Profile.from_dict(item) for item in accounts_data["data"]]

    return profile_objects
