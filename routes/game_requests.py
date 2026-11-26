from flask import Blueprint, request, jsonify
from db import get_db_connection

game_requests_bp = Blueprint("game_requests", __name__, url_prefix="/game_requests")

@game_requests_bp.route("", methods=["POST"])
def create_game_request():
    data = request.get_json()
    
    user_id = data.get("user_id")
    title = data.get("title")
    description = data.get("description")
    genre = data.get("genre")
    tags = data.get("tags")
    platform = data.get("platform")
    release_year = data.get("release_year")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("INSERT INTO game_requests (user_id, title, description, genre, tags, platform, release_year) VALUES (?, ?, ?, ?, ?, ?, ?)",
                     (user_id, title, description, genre, tags, platform, release_year))
    
    game_requests_id = cursor.lastrowid
    conn.commit()
    
    conn.close()
    
    return jsonify({
        "id": game_requests_id,
        "user_id": user_id,
        "title": title,
        "description": description,
        "genre": genre,
        "tags": tags,
        "platform": platform,
        "release_year": release_year
    }), 201
    
@game_requests_bp.route("", methods=["GET"])
def get_game_requests():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM game_requests ORDER BY id DESC")
    game_requests = cursor.fetchall()
    
    conn.close()
    
    return jsonify([dict(game_request) for game_request in game_requests]), 200

@game_requests_bp.route("/<int:game_request_id>", methods=["GET"])
def get_game_request(game_request_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM game_requests WHERE id = ?", (game_request_id,))
    game_request = cursor.fetchone()
    
    conn.close()
    
    return jsonify(dict(game_request)), 200

@game_requests_bp.route("/<int:game_request_id>", methods=["PATCH"])
def update_game_request(game_request_id):
    data = request.get_json()
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(f"UPDATE game_requests SET {', '.join(f'{key} = ?' for key in data)} WHERE id = ?", (*data.values(), game_request_id))
    conn.commit()
    
    cursor.execute("SELECT * FROM game_requests WHERE id = ?", (game_request_id,))
    game_request = cursor.fetchone()
    
    conn.close()
    
    return jsonify(dict(game_request)), 200

@game_requests_bp.route("/<int:game_request_id>", methods=["DELETE"])
def delete_game_request(game_request_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM game_requests WHERE id = ?", (game_request_id,))
    conn.commit()
    
    conn.close()
    
    return jsonify({"message": "Игровой запрос успешно удалён"}), 200