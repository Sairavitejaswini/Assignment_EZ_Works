import base64
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from db import mysql

client_bp = Blueprint('client', __name__)

# List all files
@client_bp.route('/files', methods=['GET'])
@jwt_required()
def list_files():
    current_user = get_jwt_identity()
    if current_user['role'] != 'client':
        return jsonify({"message": "Access denied"}), 403

    cur = mysql.connection.cursor()
    cur.execute("SELECT id, filename FROM files")
    files = cur.fetchall()
    cur.close()

    return jsonify({"files": [{"id": f[0], "filename": f[1]} for f in files]}), 200

# Generate Secure Download Link
@client_bp.route('/download/<int:file_id>', methods=['GET'])
@jwt_required()
def generate_download_link(file_id):
    current_user = get_jwt_identity()
    if current_user['role'] != 'client':
        return jsonify({"message": "Access denied"}), 403

    cur = mysql.connection.cursor()
    cur.execute("SELECT filename FROM files WHERE id = %s", (file_id,))
    file = cur.fetchone()
    cur.close()

    if not file:
        return jsonify({"message": "File not found"}), 404

    encrypted_link = base64.urlsafe_b64encode(file[0].encode()).decode()
    return jsonify({"download_url": f"http://127.0.0.1:5000/client/download-file/{encrypted_link}"}), 200

# Download File
@client_bp.route('/download-file/<string:encrypted_link>', methods=['GET'])
@jwt_required()
def download_file(encrypted_link):
    try:
        filename = base64.urlsafe_b64decode(encrypted_link).decode()
    except Exception:
        return jsonify({"message": "Invalid download link"}), 400

    file_path = os.path.join("uploads", filename)
    if os.path.exists(file_path):
        return jsonify({"message": "File ready for download", "path": file_path}), 200
    else:
        return jsonify({"message": "File not found"}), 404
