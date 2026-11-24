from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash
from db import get_db_connection

users_bp = Blueprint("users", __name__, url_prefix="/users")

@users_bp.route("/register", methods=["POST"])
def register_user():
    data = request.get_json(force=True)
    
    username = data.get("username")
    email = data.get("email")
    password_hash = generate_password_hash(data.get("password"))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)", (username, email, password_hash))
    conn.commit()
    user_id = cursor.lastrowid
    
    conn.close()
    
    return jsonify({
        "id": user_id,
        "username": username,
        "email": email
    }), 201
    
@users_bp.route("", methods=["GET"])
def get_users():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, username, email, created_at FROM users")
    users = cursor.fetchall()
    
    conn.close()
    
    return jsonify([dict(user) for user in users]), 200

@users_bp.route("/<int:user_id>", methods=["GET"])
def get_user(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, username, email, created_at FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    
    conn.close()
    
    return jsonify(dict(user)), 200

@users_bp.route("/<int:user_id>", methods=["PATCH"])
def update_user(user_id):
    data = request.get_json(force=True)
    
    username = data.get("username")
    email = data.get("email")
    password_hash = generate_password_hash(data.get("password"))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("UPDATE users SET username = ?, email = ?, password_hash = ? WHERE id = ?", (username, email, password_hash, user_id))
    conn.commit()
    
    conn.close()
    
    return jsonify({
        "id": user_id,
        "username": username,
        "email": email
    }), 200
    
@users_bp.route("/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    
    conn.close()
    
    return jsonify({"message": "Пользователь успешно удалён"}), 200