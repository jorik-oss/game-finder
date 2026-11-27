from flask import Blueprint, request, jsonify
from db import get_db_connection

replies_bp = Blueprint("replies", __name__, url_prefix="/replies")

@replies_bp.route("", methods=["POST"])
def create_reply():
    data = request.get_json()
    
    user_id = data.get("user_id")
    request_id = data.get("request_id")
    parent_reply_id = data.get("parent_reply_id")
    message = data.get("message")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("INSERT INTO replies (user_id, request_id, parent_reply_id, message) VALUES (?, ?, ?, ?)",
                     (user_id, request_id, parent_reply_id, message))
    request_id = cursor.lastrowid
    conn.commit()
    
    conn.close()
    
    return jsonify({
        "request_id": request_id,
        "message": message
        }), 201

@replies_bp.route("/<int:request_id>", methods=["GET"])
def get_replies(request_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM replies WHERE request_id = ? ORDER BY id DESC", (request_id,))
    replies = cursor.fetchall()
    
    conn.close()
    
    return jsonify([dict(reply) for reply in replies]), 200

@replies_bp.route("/<int:reply_id>", methods=["PATCH"])
def update_replay(reply_id):
    data = request.get_json()
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("Update replies SET message = ? WHERE id = ?", (data.get("message"), reply_id))
    conn.commit()
    
    conn.close()
    
    return jsonify({"message": data.get("message")}), 200

@replies_bp.route("/<int:reply_id>", methods=["DELETE"])
def delete_reply(reply_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM replies WHERE id = ?", (reply_id,))
    conn.commit()
    
    conn.close()
    
    return jsonify({"message": "Ответ успешно удалён"})