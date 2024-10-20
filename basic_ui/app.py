import os
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, Integer, String
import re

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY") or "a secret key"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///networkpro.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

class Email(db.Model):
    id = Column(Integer, primary_key=True)
    email = Column(String(120), unique=True, nullable=False)

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit-email', methods=['POST'])
def submit_email():
    try:
        data = request.json
        email = data.get('email')

        if not email or not is_valid_email(email):
            return jsonify({"success": False, "message": "Invalid email address"}), 400

        existing_email = Email.query.filter_by(email=email).first()
        if existing_email:
            return jsonify({"success": False, "message": "Email already registered"}), 400

        new_email = Email(email=email)
        db.session.add(new_email)
        db.session.commit()
        return jsonify({"success": True, "message": "Email submitted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error submitting email: {str(e)}")
        return jsonify({"success": False, "message": "An error occurred while processing your request"}), 500

def is_valid_email(email):
    email_regex = re.compile(r"[^@]+@[^@]+\.[^@]+")
    return email_regex.match(email) is not None

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
