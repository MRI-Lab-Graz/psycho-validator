"""
BIDS JSON Editor - Main Entry Point
Launches Flask server and opens browser for schema-driven BIDS JSON editing
"""

import sys
import webbrowser
import threading
import time
from pathlib import Path

from src.backend.app import create_app


def open_browser(port=5000):
    """Open browser after a short delay to let Flask start"""
    time.sleep(1)
    url = f"http://localhost:{port}"
    print(f"\n✓ Opening browser: {url}")
    webbrowser.open(url)


def main():
    """Main entry point"""
    # Get BIDS folder from command line if provided
    bids_folder = None
    if len(sys.argv) > 1:
        bids_folder = sys.argv[1]
        if not Path(bids_folder).exists():
            print(f"✗ Error: BIDS folder not found: {bids_folder}")
            sys.exit(1)
        print(f"✓ BIDS folder: {bids_folder}")

    # Create Flask app
    app = create_app(bids_folder)

    # Find available port
    port = find_free_port(5000)

    # Open browser in a background thread
    browser_thread = threading.Thread(target=open_browser, args=(port,), daemon=True)
    browser_thread.start()

    # Start Flask server
    print(f"\n{'=' * 60}")
    print("BIDS JSON Editor - Schema-driven Metadata Editor")
    print(f"{'=' * 60}")
    print(f"\n🚀 Starting server on http://localhost:{port}")
    print("💡 Press Ctrl+C to stop the server\n")

    try:
        app.run(debug=False, port=port, use_reloader=False)
    except KeyboardInterrupt:
        print("\n\n✓ Server stopped. Goodbye!")
        sys.exit(0)


def find_free_port(start_port=5000, max_attempts=10):
    """Find an available port starting from start_port"""
    import socket

    for port in range(start_port, start_port + max_attempts):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.bind(("localhost", port))
            sock.close()
            return port
        except OSError:
            continue
    return start_port  # Fallback


if __name__ == "__main__":
    main()
