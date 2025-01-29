import os
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from db import mysql

ops_bp = Blueprint('ops', __name__)

UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {'pptx', 'docx', 'xlsx'}

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@ops_bp.route('/upload', methods=['POST'])
@jwt_required()
def upload_file():
    current_user = get_jwt_identity()
    if current_user['role'] != 'ops':
        return jsonify({"message": "Access denied"}), 403

    if 'file' not in request.files:
        return jsonify({"message": "No file provided"}), 400

    file = request.files['file']
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO files (filename, owner_id) VALUES (%s, %s)", (filename, current_user['id']))
        mysql.connection.commit()
        cur.close()

        return jsonify({"message": "File uploaded successfully"}), 201
    else:
        return jsonify({"message": "Invalid file type"}), 400
