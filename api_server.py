from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

# Database config (Render provides DATABASE_URL)
db_url = os.getenv("DATABASE_URL")
if db_url and db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://")
app.config["SQLALCHEMY_DATABASE_URI"] = db_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# DB Model for storing FortiAnalyzer POST events
class FabricEvent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.JSON)

# ✅ Create tables automatically (if not exists)
with app.app_context():
    db.create_all()

# Endpoint to receive FortiAnalyzer events
@app.route("/fabric-connector", methods=["POST"])
def fabric_connector():
    try:
        data = request.json
        if not data:
            return jsonify({"status": "error", "message": "No JSON payload received"}), 400

        event = FabricEvent(content=data)
        db.session.add(event)
        db.session.commit()

        return jsonify({"status": "success", "message": "Event stored"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# Endpoint to view all stored events
@app.route("/events", methods=["GET"])
def get_events():
    try:
        events = FabricEvent.query.all()
        return jsonify([{"id": e.id, "content": e.content} for e in events]), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# Health check
@app.route("/", methods=["GET"])
def home():
    return "FortiAnalyzer API Server is running ✅", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
#test
