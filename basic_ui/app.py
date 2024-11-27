import os
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

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

app = Flask(__name__)
app.static_folder = 'static'
app.static_url_path = '/static'

app.secret_key = os.environ.get("FLASK_SECRET_KEY") or "a secret key"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///networkpro.db"
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
    password_hash = Column(String(128), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    email_verified = Column(Boolean, default=False)
    name = Column(String(100))
    resume_filename = Column(String(255))  # Store the filename
    resume_content = Column(Text)          # Store the extracted text content
    resume_file_type = Column(String(10))  # Store file type (pdf/doc/docx)
    career_interest = Column(String(1000))
    key_accomplishments = Column(String(2000))
    relevant_content = Column(String(2000))

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

    def save_resume(self, file):
        """Handle resume file upload and text extraction"""
        try:
            # Generate secure filename
            filename = secure_filename(file.filename)
            file_ext = filename.rsplit('.', 1)[1].lower()
            
            if file_ext not in ['pdf', 'doc', 'docx']:
                raise ValueError("Invalid file type. Only PDF and Word documents are allowed.")
            
            # Save file to disk
            upload_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(upload_path)
            
            # Extract text from file
            if file_ext == 'pdf':
                text = extract_text_from_pdf(upload_path)
            else:
                text = extract_text_from_word(upload_path)
            
            # Update user record
            self.resume_filename = filename
            self.resume_content = text
            self.resume_file_type = file_ext
            
            return True
            
        except Exception as e:
            app.logger.error(f"Error saving resume: {str(e)}")
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
            # Handle file upload
            if 'resume' not in request.files:
                return jsonify({"success": False, "message": "No resume file provided"}), 400
                
            resume_file = request.files['resume']
            if resume_file.filename == '':
                return jsonify({"success": False, "message": "No selected file"}), 400

            # Get other form data
            data = request.form
            email = data.get('email')
            password = data.get('password')

            if not email or not is_valid_email(email):
                return jsonify({"success": False, "message": "Invalid email address"}), 400

            # Create new user
            new_user = User(
                email=email,
                name=data.get('name'),
                career_interest=data.get('career_interest')
            )
            new_user.set_password(password)
            
            # Handle resume upload
            if not new_user.save_resume(resume_file):
                return jsonify({"success": False, "message": "Error processing resume file"}), 400

            db.session.add(new_user)
            db.session.commit()

            login_user(new_user)
            return jsonify({"success": True, "message": "Account created successfully"}), 200
            
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Error creating user: {str(e)}")
            return jsonify({"success": False, "message": str(e)}), 500

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
        # Get the request data
        request_data = request.json
        
        # Validate required fields
        if not request_data.get('contact_info', {}).get('name'):
            return jsonify({
                "success": False,
                "message": "Contact name is required"
            }), 400
            
        if not request_data.get('contact_info', {}).get('company'):
            return jsonify({
                "success": False,
                "message": "Contact company is required"
            }), 400
        
        # Add logging before the API call
        logging.info(f"Generating email with request data: {request_data}")
        
        try:
            # Call the email generation API
            response = requests.post(
                'http://localhost:8002/generate-email',
                json=request_data,
                timeout=360
            )
            
            logging.info(f"Received response from API with status code: {response.status_code}")
            
            response.raise_for_status()
            email_data = response.json()
            logging.info("Successfully processed email response")
        except requests.exceptions.RequestException as e:
            logging.error(f"API request failed: {str(e)}")
            return jsonify({'error': f'API request failed: {str(e)}'}), 500
        except ValueError as e:
            logging.error(f"JSON decode error: {str(e)}")
            return jsonify({'error': 'Invalid response format from API'}), 500
        except Exception as e:
            logging.error(f"Unexpected error: {str(e)}")
            return jsonify({'error': f'An unexpected error occurred: {str(e)}'}), 500
        
        # Store the email in EmailHistory
        new_email_history = EmailHistory(
            user_id=current_user.id,
            contact_name=request_data['contact_info']['name'],
            contact_company=request_data['contact_info']['company'],
            email_draft=email_data.get('email_draft')
        )
        
        db.session.add(new_email_history)
        db.session.commit()
        
        return jsonify(email_data)

            
    except requests.RequestException as e:
        app.logger.error(f"API Error: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Error connecting to email generation service. Please ensure the service is running and try again."
        }), 500
    except Exception as e:
        app.logger.error(f"Error: {str(e)}")
        return jsonify({
            "success": False,
            "message": "An unexpected error occurred"
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
        return '', 404

if __name__ == '__main__':
    app.run()
