from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import os
import requests

app = Flask(__name__)

# Database configuration
db_url = os.getenv("DATABASE_URL")
if db_url and db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://")
app.config["SQLALCHEMY_DATABASE_URI"] = db_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# Database model for storing FortiAnalyzer POST events
class FabricEvent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.JSON)

# Create tables automatically
with app.app_context():
    db.create_all()

# Endpoint to receive FortiAnalyzer events and forward them
@app.route("/fabric-connector", methods=["POST"])
def fabric_connector():
    try:
        data = request.json
        if not data:
            return jsonify({"status": "error", "message": "No JSON payload received"}), 400

        # Store the event locally
        event = FabricEvent(content=data)
        db.session.add(event)
        db.session.commit()

        # Forward the same data to Azure Logic App
        forward_url = (
            "https://prod-20.westeurope.logic.azure.com:443/workflows/"
            "558bfb739e4e4ed7aec4772f9e20f971/triggers/manual/paths/invoke"
            "?api-version=2016-06-01&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&"
            "sig=yZ4vh-0J2QlsKZtJH_IkJ_rBM0-iIRpO3maWs5XnAbE"
        )
        forward_response = requests.post(forward_url, json=data)

        if forward_response.status_code == 200:
            return jsonify({"status": "success", "message": "Event stored and forwarded"}), 200
        else:
            return jsonify({
                "status": "partial_success",
                "message": "Event stored, but forwarding failed",
                "forward_status": forward_response.status_code,
                "forward_response": forward_response.text
            }), 202

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

# Health check endpoint
@app.route("/", methods=["GET"])
def home():
    return "FortiAnalyzer API Server is running ✅", 200
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
