
# AI-Powered Internal Information Retrieval Chatbot

This project is an AI-driven chatbot designed to assist employees with retrieving information from internal HR documents using natural language queries. Developed as part of a Master's thesis, the chatbot integrates OpenAI's GPT-3.5 Turbo with a custom document database.

## 🚀 Features

- Natural language interface for querying internal HR policies and documents
- Integration with OpenAI GPT-3.5 Turbo via API
- Custom MySQL backend for document storage and retrieval
- Lightweight, responsive web interface
- Admin panel for uploading and managing documents
- User feedback collection and rating system

## 🧠 Technology Stack

- **Frontend:** HTML5, CSS, JavaScript
- **Backend:** Python (Flask), Gunicorn
- **Database:** MySQL
- **AI Integration:** OpenAI GPT-3.5 Turbo API

## 📁 Project Structure

```
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
```

## 💾 Setup Instructions

1. Clone the repository:
   ```bash
   git clone https://github.com/Mistergpofficial/masters.git
   cd masters
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up your OpenAI API key in your environment variables.

4. Start the Flask app:
   ```bash
   python main.py
   ```

## 📸 Screenshots

Refer to the appendix folder (if included) for screenshots showing sample chatbot interactions and database structure.

## 📄 License

This project is licensed under the MIT License.
