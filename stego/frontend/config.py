"""All frontend constants"""

from pathlib import Path

# Paths
file_path = Path(__file__).resolve()

ROOT = file_path.parent

TEMPLATES_PATH = ROOT / "templates"
STATIC_PATH = ROOT / "static"

TRITON_URL = "stego_network_stego-backend"
TRITON_PORT = 8001

# Constants
PORT = 8080
