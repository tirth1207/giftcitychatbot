from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
from dotenv import load_dotenv
# from openai import OpenAI, OpenAIError  # Commented out OpenAI

def get_user_said():
    return "User said something"

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chatbot.db'
db = SQLAlchemy(app)

# Setup LoginManager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Configure OpenAI - Commented out
# try:
#     api_key = os.getenv('OPENAI_API_KEY')
#     if not api_key:
#         raise ValueError("No OpenAI API key found. Please set OPENAI_API_KEY in your .env file")
    
#     client = OpenAI()  # It will automatically use OPENAI_API_KEY from environment
    
#     # Test the API key with a simple request
#     test_response = client.chat.completions.create(
#         model="gpt-3.5-turbo",
#         messages=[{"role": "user", "content": "test"}],
#         max_tokens=5
#     )
#     print("OpenAI API connection successful")
    
# except Exception as e:
#     print(f"Error initializing OpenAI client: {str(e)}")
#     raise

# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    conversations = db.relationship('Conversation', backref='user', lazy=True)

class Conversation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    messages = db.relationship('Message', backref='conversation', lazy=True)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey('conversation.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    role = db.Column(db.String(10), nullable=False)  # 'user' or 'assistant'
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def index():
    if current_user.is_authenticated:
        return render_template('chat.html')
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('index'))
        flash('Invalid username or password')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return redirect(url_for('register'))
        
        user = User(username=username, password_hash=generate_password_hash(password))
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/api/chat', methods=['POST'])
@login_required
def chat():
    data = request.json
    message = data.get('message')
    conversation_id = data.get('conversation_id')
    
    if not message:
        return jsonify({'error': 'Message is required'}), 400
    
    try:
        if not conversation_id:
            # Create new conversation
            conversation = Conversation(user_id=current_user.id)
            db.session.add(conversation)
            db.session.commit()
            conversation_id = conversation.id
        else:
            conversation = Conversation.query.get_or_404(conversation_id)
            if conversation.user_id != current_user.id:
                return jsonify({'error': 'Unauthorized'}), 403
        
        # Save user message
        user_message = Message(
            conversation_id=conversation_id,
            content=message,
            role='user'
        )
        db.session.add(user_message)
        
        # Create simple echo response
        response = f"You said: {message}"
        
        # Save echo response
        ai_message = Message(
            conversation_id=conversation_id,
            content=response,
            role='assistant'
        )
        db.session.add(ai_message)
        db.session.commit()
        
        return jsonify({
            'response': response,
            'conversation_id': conversation_id
        })
            
    except Exception as e:
        print(f"Server Error: {str(e)}")
        db.session.rollback()
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

@app.route('/api/conversations')
@login_required
def get_conversations():
    conversations = Conversation.query.filter_by(user_id=current_user.id).order_by(Conversation.timestamp.desc()).all()
    return jsonify([{
        'id': conv.id,
        'timestamp': conv.timestamp.isoformat(),
        'preview': conv.messages[0].content[:50] + '...' if conv.messages else 'Empty conversation'
    } for conv in conversations])

@app.route('/api/conversation/<int:conversation_id>')
@login_required
def get_conversation(conversation_id):
    conversation = Conversation.query.get_or_404(conversation_id)
    if conversation.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    messages = [{
        'content': msg.content,
        'role': msg.role,
        'timestamp': msg.timestamp.isoformat()
    } for msg in conversation.messages]
    
    return jsonify(messages)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True) 
