"""
Flask Blueprint Adapter for JSON Editor
Converts the standalone JSON Editor app into a reusable Flask blueprint
that can be integrated into the main psycho-validator web interface.
"""

from flask import Blueprint, render_template, request, jsonify
from pathlib import Path
import sys

# Import JSON editor components
try:
    # Add json_editor src to path for imports
    # Use absolute path from the repo root
    json_editor_src = Path(__file__).parent / "json_editor" / "src"
    abs_path = json_editor_src.resolve()
    if str(abs_path) not in sys.path:
        sys.path.insert(0, str(abs_path))

    print(f"📝 JSON Editor path: {abs_path}")

    # Now import from the json_editor src
    from backend.file_manager import FileManager
    from backend.json_validator import JSONValidator
    from schema_loader import BIDSSchemaLoader

    print("✓ JSON Editor components imported successfully")
except ImportError as e:
    print(f"⚠️  Warning: Could not import JSON editor components: {e}")
    import traceback

    traceback.print_exc()
    FileManager = None
    JSONValidator = None
    BIDSSchemaLoader = None


def create_json_editor_blueprint(bids_folder=None):
    """
    Create a Flask blueprint for the JSON editor

    Args:
        bids_folder: Optional path to BIDS dataset folder

    Returns:
        Flask Blueprint configured for JSON editing
    """
    bp = Blueprint(
        "json_editor",
        __name__,
        url_prefix="/editor",
        template_folder=str(Path(__file__).parent.parent / "templates"),
        static_folder=str(Path(__file__).parent / "json_editor" / "src" / "frontend"),
        static_url_path="/static",
    )

    # Store reference for use in route handlers
    bp.template_folder_path = Path(__file__).parent / "json_editor" / "src" / "frontend"

    # Initialize managers if available
    if FileManager and JSONValidator and BIDSSchemaLoader:
        file_manager = FileManager(bids_folder)
        validator = JSONValidator()
        schema_loader = BIDSSchemaLoader()

        # Load schema on startup
        try:
            schema_loader.load_schema()
        except Exception as e:
            print(f"⚠️  Warning: Could not load BIDS schema: {e}")
    else:
        file_manager = None
        validator = None
        schema_loader = None

    # ==================== BLUEPRINT ROUTES ====================

    @bp.route("/")
    @bp.route("/index.html")
    def editor_index():
        """Serve JSON editor main page with unified layout"""
        try:
            # Use the new unified template that inherits from base.html
            return render_template("json_editor.html")

        except Exception as e:
            print(f"⚠️  [JSON EDITOR] Could not render template: {e}")
            import traceback

            traceback.print_exc()
            return (
                f"""
            <html>
            <head><title>Error</title></head>
            <body>
            <h1>JSON Editor - Error Loading</h1>
            <p><strong>Error:</strong> {e}</p>
            <hr>
            <p><strong>Debug Info:</strong></p>
            <pre>{traceback.format_exc()}</pre>
            </body>
            </html>
            """,
                500,
            )

    @bp.route("/api/schema/<json_type>", methods=["GET"])
    def get_schema(json_type):
        """Get schema for specific BIDS JSON type"""
        if not schema_loader:
            return (
                jsonify({"success": False, "error": "Schema loader not available"}),
                503,
            )

        try:
            schema_def = schema_loader.get_schema_for_type(json_type)
            return jsonify({"success": True, "schema": schema_def})
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 400

    @bp.route("/api/files", methods=["GET"])
    def list_files():
        """List available BIDS JSON files"""
        if not file_manager:
            return (
                jsonify({"success": False, "error": "File manager not available"}),
                503,
            )

        try:
            files = file_manager.list_available_files()
            return jsonify({"success": True, "files": files})
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 400

    @bp.route("/api/file/<json_type>", methods=["GET"])
    def load_file(json_type):
        """Load a BIDS JSON file"""
        if not file_manager:
            return (
                jsonify({"success": False, "error": "File manager not available"}),
                503,
            )

        try:
            data = file_manager.load_file(json_type)
            return jsonify({"success": True, "data": data})
        except FileNotFoundError as e:
            return jsonify({"success": False, "error": str(e)}), 404
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 400

    @bp.route("/api/file/<json_type>", methods=["POST"])
    def save_file(json_type):
        """Save a BIDS JSON file"""
        if not file_manager:
            return (
                jsonify({"success": False, "error": "File manager not available"}),
                503,
            )

        try:
            data = request.get_json()
            if not data:
                return (
                    jsonify({"success": False, "error": "No JSON data provided"}),
                    400,
                )

            file_manager.save_file(json_type, data)

            # Validate after save
            if validator:
                errors = validator.validate(data, json_type)
                return jsonify(
                    {
                        "success": True,
                        "message": "File saved successfully",
                        "validation_errors": errors if errors else None,
                    }
                )
            else:
                return jsonify({"success": True, "message": "File saved successfully"})
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 400

    @bp.route("/api/validate", methods=["POST"])
    def validate_json():
        """Validate BIDS JSON data against schema"""
        if not validator:
            return jsonify({"success": False, "error": "Validator not available"}), 503

        try:
            data = request.get_json()
            json_type = request.args.get("type", "dataset_description")

            if not data:
                return (
                    jsonify({"success": False, "error": "No JSON data provided"}),
                    400,
                )

            errors = validator.validate(data, json_type)
            return jsonify(
                {
                    "success": True,
                    "valid": len(errors) == 0,
                    "errors": errors if errors else [],
                }
            )
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 400

    @bp.route("/api/status", methods=["GET"])
    def editor_status():
        """Return status of JSON editor components"""
        return jsonify(
            {
                "available": True,
                "file_manager": file_manager is not None,
                "validator": validator is not None,
                "schema_loader": schema_loader is not None,
                "bids_folder": str(bids_folder) if bids_folder else None,
            }
        )

    return bp
