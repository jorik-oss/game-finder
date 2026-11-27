from flask import Blueprint, request, jsonify
from db import get_db_connection

notifications_bp = Blueprint("notifications", __name__, url_prefix="/notifications")

@notifications_bp.route("", methods=["POST"])
def create_notification():
    data = request.get_json()
    
    user_id = data.get("user_id")
    sender_id = data.get("sender_id")
    reply_id = data.get("reply_id")
    chat_message_id = data.get("chat_message_id")
    message = data.get("message")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("INSERT INTO notifications (user_id, sender_id, reply_id, chat_message_id, message) VALUES (?, ?, ?, ?, ?)",
                     (user_id, sender_id, reply_id, chat_message_id, message))
    conn.commit()
    
    conn.close()
    
    return jsonify({"message": "Уведомление успешно создано"}), 201

@notifications_bp.route("/<int:user_id>", methods=["GET"])
def get_notifications(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM notifications WHERE user_id = ? ORDER BY id DESC", (user_id,))
    notifications = cursor.fetchall()
    
    cursor.execute("UPDATE notifications SET is_read = 1 WHERE user_id = ?", (user_id,))
    conn.close()
    
    return jsonify([dict(notification) for notification in notifications]), 200
       