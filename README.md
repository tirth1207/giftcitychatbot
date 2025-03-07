# ChatBot Application

A modern chatbot application with ChatGPT integration, user authentication, and conversation history.

## Features

- User authentication (login/logout)
- Chat with GPT-powered AI
- Conversation history
- Dark/Light mode toggle
- Responsive design with sidebar
- Secure API key handling

## Setup Instructions

1. Clone this repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Create a `.env` file in the root directory with:
   ```
   OPENAI_API_KEY=your_api_key_here
   SECRET_KEY=your_secret_key_here
   ```
5. Initialize the database:
   ```bash
   python init_db.py
   ```
6. Run the application:
   ```bash
   python app.py
   ```
7. Open http://localhost:5000 in your browser

## Project Structure

```
├── app.py              # Main Flask application
├── init_db.py          # Database initialization script
├── static/             # Static files (CSS, JS)
├── templates/          # HTML templates
└── instance/           # Database file location
``` 