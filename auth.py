from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token
from db import mysql

auth_bp = Blueprint('auth', __name__)

# User Signup (Client)
@auth_bp.route('/signup', methods=['POST'])
def signup():
    data = request.json
    name = data['name']
    email = data['email']
    password = generate_password_hash(data['password'])

    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO users (name, email, password, role) VALUES (%s, %s, %s, 'client')", (name, email, password))
    mysql.connection.commit()
    cur.close()

    return jsonify({"message": "User created successfully"}), 201

# User Login
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data['email']
    password = data['password']

    cur = mysql.connection.cursor()
    cur.execute("SELECT id, password, role FROM users WHERE email = %s", (email,))
    user = cur.fetchone()
    cur.close()

    if user and check_password_hash(user[1], password):
        access_token = create_access_token(identity={"id": user[0], "role": user[2]})
        return jsonify(access_token=access_token), 200
    else:
        return jsonify({"message": "Invalid credentials"}), 401
