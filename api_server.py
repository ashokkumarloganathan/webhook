from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import os
 
app = Flask(__name__)
 
# Render gives DATABASE_URL as env variable when you link a Postgres instance
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL").replace("postgres://", "postgresql://")
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
 
if __name__ == "__main__":
app.run(host="0.0.0.0", port=5000)