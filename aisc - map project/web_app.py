"""
MUJ Campus AI Navigator - Lightweight, Cute Modern Web Application.
Serves an aesthetic, pastel geospatial visualization and heuristic search dashboard.
Preserves the underlying AISC search engine, spatial graph, and dynamic models without disruption.
"""

import os
import sys
import webbrowser
from threading import Timer

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from api.index import app

if __name__ == "__main__":
    PORT = 5000
    print("=" * 70)
    print(" 🌸 MUJ AI Campus Navigator - Cute Web Interface Starting...")
    print(f" 🌐 URL: http://127.0.0.1:{PORT}")
    print("=" * 70)
    
    Timer(1.2, lambda: webbrowser.open(f"http://127.0.0.1:{PORT}")).start()
    app.run(host="127.0.0.1", port=PORT, debug=False)
