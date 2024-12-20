import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify, redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey
import re
import requests
from datetime import datetime
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import json
from werkzeug.utils import secure_filename
from PyPDF2 import PdfReader
from docx import Document
import tempfile
import logging

logging.basicConfig(level=logging.INFO)

load_dotenv()

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

app = Flask(__name__)
app.static_folder = 'static'
app.static_url_path = '/static'

app.secret_key = os.environ.get("FLASK_SECRET_KEY") or "a secret key"
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Create uploads directory if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    email = Column(String(120), unique=True, nullable=False)
    password_hash = Column(String(512), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    email_verified = Column(Boolean, default=False)
    name = Column(String(100))
    resume_content = Column(Text)          # Store the extracted text content
    career_interest = Column(String(1000))
    key_accomplishments = Column(String(2000))
    relevant_content = Column(String(2000))
    resume_text = Column(Text)  # New field

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def set_key_accomplishments(self, accomplishments_list):
        """Convert list to JSON string for storage"""
        self.key_accomplishments = json.dumps(accomplishments_list)

    def get_key_accomplishments(self):
        """Convert stored JSON string back to list"""
        if self.key_accomplishments:
            return json.loads(self.key_accomplishments)
        return []

    def save_resume(self, resume_text):
        """Save resume text directly to database"""
        try:
            self.resume_content = resume_text
            return True
        except Exception as e:
            app.logger.error(f"Error saving resume text: {str(e)}")
            return False

class EmailHistory(db.Model):
    __tablename__ = 'email_history'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    contact_name = Column(String(100), nullable=False)
    contact_company = Column(String(100), nullable=False)
    email_draft = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect('/dashboard')

    if request.method == 'POST':
        data = request.json
        user = User.query.filter_by(email=data.get('email')).first()
        
        if user and user.check_password(data.get('password')):
            login_user(user)
            return jsonify({"success": True, "message": "Login successful"}), 200
        return jsonify({"success": False, "message": "Invalid email or password"}), 401

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect('/dashboard')

    if request.method == 'POST':
        try:
            data = request.form
            app.logger.info(f"Received signup data: {data}")
            
            # Log field values
            app.logger.info(f"Email: {data.get('email')}")
            app.logger.info(f"Name: {data.get('name')}")
            app.logger.info(f"Career interest: {data.get('career_interest')}")
            app.logger.info(f"Resume text length: {len(data.get('resume_text', ''))}")

            email = data.get('email', '').strip()
            password = data.get('password', '').strip()
            name = data.get('name', '').strip()
            career_interest = data.get('career_interest', '').strip()
            resume_text = data.get('resume_text', '').strip()  # New field

            # Validate required fields
            if not all([email, password, name, resume_text]):  # Added resume_text to required fields
                return jsonify({
                    "success": False, 
                    "message": "Please fill in all required fields"
                }), 400

            # Create new user
            app.logger.info("Creating new user object")
            new_user = User(
                email=email,
                name=name,
                career_interest=career_interest,
                resume_text=resume_text  # Save the text directly
            )
            
            app.logger.info("Setting password hash")
            new_user.set_password(password)
            
            app.logger.info("Attempting database operations")
            db.session.add(new_user)
            db.session.commit()
            app.logger.info("Database commit successful")

            app.logger.info("Logging in new user")
            login_user(new_user)
            app.logger.info("User logged in successfully")

            return jsonify({
                "success": True, 
                "message": "Account created successfully",
                "redirect": "/dashboard"
            }), 200
            
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Error in signup: {str(e)}")
            app.logger.error(f"Error type: {type(e)}")
            app.logger.exception("Full traceback:")
            return jsonify({
                "success": False, 
                "message": f"An unexpected error occurred: {str(e)}"
            }), 500

    return render_template('signup.html')

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

        new_email = Email(
            email=email,
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            company=data.get('company'),
            job_title=data.get('job_title'),
            linkedin_url=data.get('linkedin_url')
        )
        db.session.add(new_email)
        db.session.commit()
        return jsonify({"success": True, "message": "Information submitted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error submitting data: {str(e)}")
        return jsonify({"success": False, "message": "An error occurred while processing your request"}), 500
    

@app.route('/check')
def check_page():
    return render_template('check_db.html')

@app.route('/check-db')
def check_db():
    try:
        db_data = {}
        # Instead of making a local request, either:
        # 1. Use an environment variable for the API endpoint
        api_url = os.environ.get('EMAIL_API_URL', 'https://your-api-url.com/generate-email')
        try:
            response = requests.post(api_url)
            response.raise_for_status()
            email_data = response.json()
            db_data['generated_email'] = email_data.get('email_draft')
        except requests.RequestException as e:
            db_data['generated_email'] = f"Error generating email: {str(e)}"
            
        return jsonify(db_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def is_valid_email(email):
    email_regex = re.compile(r"[^@]+@[^@]+\.[^@]+")
    return email_regex.match(email) is not None

@app.route('/generate-email', methods=['GET', 'POST'])
@login_required
def generate_email():
    if request.method == 'GET':
        return render_template('generate_email.html')
        
    try:
        request_data = request.json
        app.logger.info(f"Generate email request data: {request_data}")
        
        if not request_data.get('contact_info', {}).get('name'):
            app.logger.error("Missing contact name")
            return jsonify({
                "success": False,
                "message": "Contact name is required"
            }), 400
            
        if not request_data.get('contact_info', {}).get('company'):
            app.logger.error("Missing company name")
            return jsonify({
                "success": False,
                "message": "Contact company is required"
            }), 400
        
        app.logger.info("Calling email generation API")
        CLOUD_RUN_URL = "https://email-agent-1085470808659.us-west2.run.app/generate-email"
        
        try:
            app.logger.info(f"Making request to: {CLOUD_RUN_URL}")
            response = requests.post(
                CLOUD_RUN_URL,
                json=request_data,
                timeout=360,
                headers={'Content-Type': 'application/json'}
            )
            
            app.logger.info(f"API response status: {response.status_code}")
            app.logger.info(f"API response: {response.text[:500]}...")  # Log first 500 chars
            
            response.raise_for_status()
            email_data = response.json()
            app.logger.info("Successfully processed email response")
            
        except requests.exceptions.RequestException as e:
            app.logger.error(f"API request failed: {str(e)}")
            return jsonify({'error': f'API request failed: {str(e)}'}), 500
            
        except ValueError as e:
            app.logger.error(f"JSON decode error: {str(e)}")
            return jsonify({'error': 'Invalid response format from API'}), 500
            
        except Exception as e:
            app.logger.error(f"Unexpected error in API call: {str(e)}")
            app.logger.exception("Full traceback:")
            return jsonify({'error': f'An unexpected error occurred: {str(e)}'}), 500

        app.logger.info("Storing email in history")
        new_email_history = EmailHistory(
            user_id=current_user.id,
            contact_name=request_data['contact_info']['name'],
            contact_company=request_data['contact_info']['company'],
            email_draft=email_data.get('email_draft')
        )
        
        db.session.add(new_email_history)
        db.session.commit()
        app.logger.info("Email history stored successfully")
        
        return jsonify(email_data)

    except Exception as e:
        app.logger.error(f"Error in generate_email: {str(e)}")
        app.logger.error(f"Error type: {type(e)}")
        app.logger.exception("Full traceback:")
        return jsonify({
            "success": False,
            "message": f"An unexpected error occurred: {str(e)}"
        }), 500

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

def extract_text_from_pdf(file_path):
    """Extract text from PDF file"""
    with open(file_path, 'rb') as file:
        reader = PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
    return text

def extract_text_from_word(file_path):
    """Extract text from Word document"""
    doc = Document(file_path)
    text = ""
    for paragraph in doc.paragraphs:
        text += paragraph.text + "\n"
    return text

@app.route('/send-email', methods=['POST'])
def send_email():
    logging.info("Send email endpoint called")
    try:
        # Get the email data from the request
        email_data = request.get_json()
        
        # Call the Node.js email service
        response = requests.post(
            'http://localhost:8003/send-email',  # Note the port matches your Node.js server
            json={
                'recipientEmail': email_data.get('recipientEmail'),
                'emailDraft': email_data.get('emailDraft')
            },
            timeout=30
        )
        
        logging.info(f"Email service response status: {response.status_code}")
        
        # Raise an exception for bad status codes
        response.raise_for_status()
        
        # Return the response from the email service
        return jsonify(response.json()), response.status_code
        
    except requests.exceptions.RequestException as e:
        logging.error(f"Error calling email service: {str(e)}")
        return jsonify({'error': f'Failed to send email: {str(e)}'}), 500
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        return jsonify({'error': f'Failed to send email: {str(e)}'}), 500

@app.route('/static/<path:filename>')
def serve_static(filename):
    try:
        return app.send_static_file(filename)
    except Exception as e:
        app.logger.error(f"Error serving static file {filename}: {str(e)}")
        return jsonify({
            "error": "Failed to serve static file",
            "details": str(e)
        }), 500

@app.errorhandler(500)
def handle_error(error):
    app.logger.error(f"Internal error: {error}")
    return jsonify({
        "error": "Internal server error",
        "details": str(error)
    }), 500

if __name__ == '__main__':
    app.run()
