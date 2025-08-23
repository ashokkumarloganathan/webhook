from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

# DB Config
db_url = os.getenv("DATABASE_URL")
if db_url and db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://")
app.config["SQLALCHEMY_DATABASE_URI"] = db_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# Define Model
class FabricEvent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.JSON)

# ✅ Create tables if they don’t exist
with app.app_context():
    db.create_all()

# Routes
@app.route("/fabric", methods=["POST"])
def receive_event():
    data = request.get_json()
    event = FabricEvent(content=data)
    db.session.add(event)
    db.session.commit()
    return {"status": "success"}, 201

@app.route("/events", methods=["GET"])
def list_events():
    events = FabricEvent.query.all()
    return jsonify([{"id": e.id, "content": e.content} for e in events])
