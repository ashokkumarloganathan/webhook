from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import os
 
app = Flask(__name__)
 
# Handle DATABASE_URL from Render (safe replacement for postgres:// → postgresql://)
db_url = os.getenv("DATABASE_URL", "")
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)
 
app.config["SQLALCHEMY_DATABASE_URI"] = db_url or "sqlite:///local.db"  # fallback for local testing
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
 
db = SQLAlchemy(app)
 
# DB Model for storing FortiAnalyzer POST events
class FabricEvent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.JSON)
 
# API endpoint to receive FortiAnalyzer events
@app.route("/fabric-connector", methods=["POST"])
def fabric_connector():
    try:
        data = request.json
        event = FabricEvent(content=data)
        db.session.add(event)
        db.session.commit()
        return jsonify({"status": "success", "message": "Event stored"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400
 
# Simple health check
@app.route("/", methods=["GET"])
def home():
    return "FortiAnalyzer API Server is running ✅", 200
 
# Create tables automatically on startup
with app.app_context():
    db.create_all()
 
if __name__ == "__main__":
    # For local testing only; Render will use Gunicorn
 app.run(host="0.0.0.0", port=5000)
