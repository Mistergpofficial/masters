# AI-Powered Internal Information Retrieval Chatbot

This is an AI-driven chatbot application built with Python (Flask) and OpenAI’s GPT-3.5 Turbo. The system allows users to query internal company documents using natural language and receive accurate, contextually relevant responses. It is designed to improve information retrieval efficiency in HR and administrative settings.

## 🚀 Features

- Natural language interface using OpenAI GPT-3.5
- Custom document ingestion via file upload
- Secure session-based interaction
- Admin panel to manage document uploads and logs
- Real-time query rating system for feedback
- Lightweight frontend with HTML, CSS, and JavaScript

## 🛠️ Tech Stack

- **Backend:** Python, Flask, OpenAI API (GPT-3.5 Turbo)
- **Frontend:** HTML5, CSS3, JavaScript
- **Session Handling:** Flask-Session
- **Web Server:** Gunicorn
- **Deployment:** WSGI via `wsgi.py`

## 📁 Project Structure

masters-main/
├── main.py                    # Main Flask application
├── wsgi.py                    # WSGI entry point for deployment
├── requirements.txt           # Python dependencies
├── gunicorn_service.sh        # Gunicorn startup script
├── .gitignore                 # Git ignored files
├── README.md                  # Project documentation
├── flask_session/             # Server-side session files
├── uploaded_documents/        # Uploaded documents storage
├── static/
│   ├── admin.css              # Styles for admin panel
│   ├── chatbot.js             # Chatbot interaction logic
│   ├── rating.js              # Rating functionality
│   ├── script.js              # Main site logic
│   ├── styles.css             # General styling
│   ├── 404.html               # Custom 404 error page
│   └── images/
│       └── logo.png           # Logo image
├── templates/
│   ├── index.html             # Chat interface
│   ├── admin_panel.html       # Admin dashboard
│   └── consent-declined.html # Fallback for no user consent



## 📦 Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/Mistergpofficial/masters.git
   cd masters

2. **Create a Virtual Environment**
   python -m venv venv
   source venv/bin/activate  # or venv\Scripts\activate on Windows

3. **Install Dependencies**
   pip install -r requirements.txt

4. **Set Your OpenAI API Key**
   Create a .env file or set an environment variable:
   export OPENAI_API_KEY="your-api-key-here"

5. **Run the Flask App**
   python main.py
   **Or use Gunicorn for production:**
   sh gunicorn_service.sh
   

