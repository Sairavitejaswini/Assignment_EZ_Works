from flask import Flask
from flask_jwt_extended import JWTManager
from db import mysql
from auth import auth_bp
from ops import ops_bp
from client import client_bp

app = Flask(__name__)

# Configure MySQL Database
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'password'
app.config['MYSQL_DB'] = 'secure_files'
app.config['JWT_SECRET_KEY'] = 'supersecret'  # Change this in production

mysql.init_app(app)
jwt = JWTManager(app)

# Register Blueprints
app.register_blueprint(auth_bp, url_prefix="/auth")
app.register_blueprint(ops_bp, url_prefix="/ops")
app.register_blueprint(client_bp, url_prefix="/client")

if __name__ == "__main__":
    app.run(debug=True)
