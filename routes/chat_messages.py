from flask import Blueprint, request, jsonify
from db import get_db_connection

chat_messages_bp = Blueprint("chat_messages", __name__, url_prefix="/chat_messages")

@chat_messages_bp.route("", methods=["POST"])
def create_chat_message():
    data = request.get_json()
    user_id = data.get("user_id")
    message = data.get("message")
    reply_to_message_id = data.get("reply_to_message_id")

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("INSERT INTO chat_messages (user_id, message, reply_to_message_id) VALUES (?, ?, ?)", (user_id, message, reply_to_message_id))
    conn.commit()

    conn.close()

    return jsonify({"message": message}), 201

@chat_messages_bp.route("", methods=["GET"])
def get_chat_messages():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM chat_messages ORDER BY id DESC")
    chat_messages = cursor.fetchall()

    conn.close()

    return jsonify([dict(chat_message) for chat_message in chat_messages]), 200

@chat_messages_bp.route("/<int:user_id>", methods=["GET"])
def get_user_messages(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM chat_messages WHERE user_id = ? ORDER BY id DESC", (user_id,))
    chat_messages = cursor.fetchall()

    conn.close()

    return jsonify([dict(chat_message) for chat_message in chat_messages]), 200

@chat_messages_bp.route("/<int:message_id>", methods=["PATCH"])
def update_message(message_id):
    data = request.get_json()

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("UPDATE chat_messages SET message = ? WHERE id = ?", (data.get("message"), message_id))
    conn.commit()

    conn.close()

    return jsonify({"message": data.get("message")}), 200

@chat_messages_bp.route("/<int:message_id>", methods=["DELETE"])
def delete_message(message_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM chat_messages WHERE id = ?", (message_id,))
    conn.commit()

    conn.close()

    return jsonify({"message": "Сообщение успешно удалено"}), 200