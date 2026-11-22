from flask import Flask
from routes.chat import chat_bp
from routes.users import users_bp
from routes.requests import requests_bp
from routes.replies import replies_bp
from routes.notifications import notifications_bp

app = Flask(__name__)
app.json.ensure_ascii = False

app.register_blueprint(chat_bp)
app.register_blueprint(users_bp)
app.register_blueprint(requests_bp)
app.register_blueprint(replies_bp)
app.register_blueprint(notifications_bp)

@app.route("/", methods=["GET"])
def home():
    return {
        "message": "Game Finder API работает!"
    }
    
if __name__ == "__main__":
    app.run(debug=True)