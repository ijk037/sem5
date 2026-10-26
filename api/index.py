import os
import sys
import traceback

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_DIR = os.path.join(ROOT_DIR, "aisc - map project")

for path in [PROJECT_DIR, ROOT_DIR, os.getcwd()]:
    if path not in sys.path and os.path.isdir(path):
        sys.path.insert(0, path)

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
