import os
import sys
import traceback

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)

# Add all relevant candidate root directories to sys.path
for candidate in [PROJECT_ROOT, CURRENT_DIR, os.getcwd()]:
    if candidate not in sys.path and os.path.isdir(candidate):
        sys.path.insert(0, candidate)

try:
    from web_app import app
except Exception as e:
    from flask import Flask, jsonify
    app = Flask(__name__)
    err_tb = traceback.format_exc()

    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    def catch_all(path):
        return jsonify({
            "status": "initialization_failed",
            "error_type": type(e).__name__,
            "error_message": str(e),
            "traceback": err_tb,
            "sys_path": sys.path,
            "cwd": os.getcwd()
        }), 500

if __name__ == "__main__":
    app.run()
