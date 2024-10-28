from flask import Flask, request, make_response, jsonify
from flask_cors import CORS
from flask_migrate import Migrate
from datetime import datetime, timezone


from models import db, Message

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

CORS(app)
migrate = Migrate(app, db)

db.init_app(app)

@app.route('/messages', methods=['GET', 'POST'])
def messages():
    if request.method == 'GET':
        # GET /messages: Return all messages ordered by created_at
        messages = Message.query.order_by(Message.created_at.asc()).all()
        return jsonify([message.to_dict() for message in messages]), 200

    elif request.method == 'POST':
        # POST /messages: Create a new message
        data = request.get_json()
        new_message = Message(
            body=data.get('body'),
            username=data.get('username'),
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        db.session.add(new_message)
        db.session.commit()
        return jsonify(new_message.to_dict()), 201

@app.route('/messages/<int:id>', methods=['GET', 'PATCH', 'DELETE'])
def messages_by_id(id):
    message = db.session.get(Message, id)
    if not message:
        return jsonify({"error": "Message not found"}), 404

    if request.method == 'GET':
        # GET /messages/<id>: Return the message by ID
        return jsonify(message.to_dict()), 200

    elif request.method == 'PATCH':
        # PATCH /messages/<id>: Update the message body
        data = request.get_json()
        if 'body' in data:
            message.body = data['body']
            message.updated_at = datetime.now(timezone.utc)  # Update the timestamp
        db.session.commit()
        return jsonify(message.to_dict()), 200

    elif request.method == 'DELETE':
        # DELETE /messages/<id>: Delete the message
        db.session.delete(message)
        db.session.commit()
        return '', 204

if __name__ == '__main__':
    app.run(port=5555)
