# profile_store.py  – bullet‑proof with pickle
import pickle
from pathlib import Path
from typing import Tuple

from browserforge.fingerprints import Fingerprint, FingerprintGenerator, Screen

_BASE = Path("camoufox_profiles")

_SCREEN_DESKTOP = Screen(min_width=1024, min_height=700)   # keeps phones/tablets out

_GEN = FingerprintGenerator(
        browser="firefox",
        device="desktop",                # ← **no mobile fingerprints**
        os=("windows", "macos"),
        screen=_SCREEN_DESKTOP,
)


def _paths(user: str) -> Tuple[Path, Path]:
    """
    Returns (profile_dir, fingerprint_file).
    """
    d = _BASE / user
    d.mkdir(parents=True, exist_ok=True)
    return d, d / "fingerprint.pkl"            # <- binary pickle now


def load_or_create_fp(user: str) -> Fingerprint:
    """
    Load a persisted Fingerprint for `user`, or generate & save a new one.
    """
    profile_dir, fp_file = _paths(user)

    if fp_file.exists():
        return pickle.loads(fp_file.read_bytes())      # 🎉 object fully intact

    fp = _GEN.generate()
    fp_file.write_bytes(pickle.dumps(fp, protocol=pickle.HIGHEST_PROTOCOL))
    return fp
