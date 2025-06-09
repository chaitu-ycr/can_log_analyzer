"""
Module to start the CAN Log Analyzer Streamlit web application.
"""

import os
import sys
import socket
import subprocess
import logging
from pathlib import Path
from typing import Optional
import argparse

logging.basicConfig(
    level=getattr(logging, os.environ.get("CAN_LOG_ANALYZER_LOGLEVEL", "INFO").upper(), logging.INFO),
    format="%(levelname)s: %(message)s"
)
logger = logging.getLogger(__name__)

class WebAppRunner:
    """Handles CLI argument parsing and launching the Streamlit web app."""

    @staticmethod
    def launch(address: Optional[str] = None, port: int = 8501) -> bool:
        """Start the Streamlit web app. Returns True if successful."""
        app_file = Path(__file__).parent / "web_app.py"
        if not app_file.is_file():
            logger.error("web_app.py not found at %s", app_file)
            return False
        bind_address = address or socket.getfqdn()
        cmd = [
            sys.executable, "-m", "streamlit", "run", str(app_file),
            "--server.address", bind_address,
            "--server.port", str(port)
        ]
        logger.debug("Running: %s", ' '.join(cmd))
        try:
            subprocess.Popen(cmd)
            logger.info("Streamlit app started at http://%s:%d", bind_address, port)
            return True
        except Exception as exc:
            logger.exception("Failed to start Streamlit app: %s", exc)
            return False

    @staticmethod
    def parse_args() -> argparse.Namespace:
        """Parse CLI arguments for server address and port."""
        parser = argparse.ArgumentParser(description="Start the CAN Log Analyzer Streamlit web application.")
        parser.add_argument("--server-address", type=str, default=None, help="Bind address (default: system FQDN)")
        parser.add_argument("--server-port", type=int, default=8501, help="Port (default: 8501)")
        return parser.parse_args()

def main():
    args = WebAppRunner.parse_args()
    if not WebAppRunner.launch(args.server_address, args.server_port):
        sys.exit(1)

if __name__ == '__main__':
    main()