from flask import Flask, render_template, request, jsonify, flash, send_file, session as flask_session
from werkzeug.utils import secure_filename
import openai
import os
from dotenv import load_dotenv
#from dotenv import dotenv_values
from PyPDF2 import PdfReader
from flask_session import Session
from pathlib import Path
import fitz
import re
from fpdf import FPDF
from datetime import datetime
import uuid
import mysql.connector
import secrets
import logging

# Set up logging configuration (add this before your route)
logging.basicConfig(level=logging.DEBUG)

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Generate a random 32-byte key and convert it to a string
strong_secret_key = secrets.token_hex(32)

# Set the Flask app's secret key
app.secret_key = strong_secret_key


app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

api_key = os.environ.get("openai_api_key")
print(api_key)

app.config['UPLOAD_FOLDER'] = 'uploaded_documents'
app.config['ALLOWED_EXTENSIONS'] = {'pdf'}

# I'm Creating the upload folder(where the policy document and FAQ is stored) if it doesn't exist
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Here I initialize session state
app.config['UPLOADED_FILES'] = []

# I'm checking if the file has a valid extension
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']



# Initialize MySQL connection
def create_db_connection():
    return mysql.connector.connect(
        host=os.environ.get("MYSQLHOST"),
        user=os.environ.get("MYSQLUSER"),
        port=os.environ.get("MYSQLPORT"),
        password=os.environ.get("MYSQLPASSWORD"),
        database=os.environ.get("MYSQLDATABASE")
    )


# Chatbot Function
def chatbot(api_key, messages, query_text, file_data_list):
    openai.api_key = api_key
    if query_text:
        messages.append({"role": "user", "content": query_text})
    for file_data in file_data_list:
        messages.append({"role": "user", "content": f"PDF File Type: {file_data}"})
    chat = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-0125", messages=messages, stream=True, temperature=0.5
    )

    response_line = ''.join(chunk['choices'][0]['delta'].get('content', '') for chunk in chat)
    response_line = clean_response(response_line)[:500]
    
    response_text = f"Response: {response_line}"
    messages.append({"role": "assistant", "content": response_line})

    return response_text

# Function to clean response and remove unnecessary information
def clean_response(response):
    response = response.strip()
    response = re.sub(r'\s+', ' ', response)
    response = re.sub(r'<.*?>', '', response)
    response = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', response)
    response = ''.join(char for char in response if char.isprintable())
    response = re.sub(r'([.,!?])\1+', r'\1', response)
    return response


# Function to check if the knowledge base PDF needs to be updated
def needs_update(folder_path, knowledge_base_folder="knowledgebase", knowledge_base_filename="knowledge_base.pdf"):
    knowledge_base_path = os.path.join(knowledge_base_folder, knowledge_base_filename)

    if not os.path.exists(knowledge_base_path):
        return True

    knowledge_base_timestamp = os.path.getmtime(knowledge_base_path)

    for file_name in os.listdir(folder_path):
        if file_name.endswith(".pdf"):
            file_path = os.path.join(folder_path, file_name)
            document_timestamp = os.path.getmtime(file_path)

            if document_timestamp > knowledge_base_timestamp:
                return True

    return False

# Function to combine PDF documents into a single PDF(our knowledgebase document)
def combine_pdfs(folder_path, knowledge_base_folder="knowledgebase", output_filename="knowledge_base.pdf"):
    pdf = FPDF()

    for file_name in os.listdir(folder_path):
        if file_name.endswith(".pdf"):
            file_path = os.path.join(folder_path, file_name)
            pdf_document = fitz.open(file_path)

            for page_num in range(pdf_document.page_count):
                page = pdf_document.load_page(page_num)
                pdf.add_page()
                pdf.set_font("Arial", size=12)

                text = page.get_text("text")
                pdf.multi_cell(0, 10, txt=text.encode("latin-1", "replace").decode("latin-1"))

            pdf_document.close()

    knowledge_base_path = os.path.join(knowledge_base_folder, output_filename)
    pdf.output(knowledge_base_path)
    return f"Knowledge base PDF created/updated as {knowledge_base_path}"

# Main Application for User
@app.route('/')
def index():
    knowledgebase_folder = "knowledgebase"
        # Initialize Flask session with messages and conversation history
    flask_session['messages'] = [{"role": "system", "content": "You are a professional Question and Answer AI Assistant helping with information in regards to HR Policy documents and FAQ."}]
    flask_session['conversation_history'] = []

    if not os.listdir(knowledgebase_folder):
        combine_pdfs("uploaded_documents", knowledgebase_folder)
        flask_session['knowledgebase_status'] = "Knowledgebase updated"
    else:
        flask_session['knowledgebase_status'] = "Knowledgebase up to date"

    print(f"Knowledgebase status: {flask_session['knowledgebase_status']}")

    # Check if 'conversation_history' exists in the session
    if 'conversation_history' not in flask_session:
        # If the conversation history doesn't exist, initialize it with the system message
        initial_system_message = {"role": "system", "content": "You are a professional Question and Answer AI Assistant helping with information in regards to HR Policy documents and FAQ."}
        flask_session['conversation_history'] = [initial_system_message]

    # Initialize visit_id if not present in the session
    if 'visit_id' not in flask_session:
        flask_session['visit_id'] = str(uuid.uuid4())

    # Initialize a dictionary to track first ratings for each question
    flask_session.setdefault('ratings', {})

    # Initialize a dictionary to track ease of use ratings after session expires
    flask_session.setdefault('easeratings', {})

    # Initialize question_id if not present in the session
    if 'question_id' not in flask_session:
        flask_session['question_id'] = str(uuid.uuid4())


    return render_template('index.html', session=flask_session, conversation_history=flask_session['conversation_history'])



# Consent Section
@app.route('/consent', methods=['POST'])
def acknowledge_consent():
    flask_session['consent_acknowledged'] = True
    return jsonify({"status": "success"})

# Ask the chatbot
@app.route('/ask', methods=['POST'])
def ask():
    data = request.get_json()
    query_text = data['query_text']

    # Check if 'conversation_history' exists in the session
    if 'conversation_history' not in flask_session:
        flask_session['conversation_history'] = []

    document_folder = "knowledgebase"

    available_documents = [file for file in os.listdir(document_folder) if file.endswith(".pdf")]

    # Extract content from all PDF documents in the folder
    file_data_list = []
    for selected_document in available_documents:
        file_path = os.path.join(document_folder, selected_document)
        try:
            pdf_document = fitz.open(file_path)
            file_data = ""
            for page_num in range(pdf_document.page_count):
                page = pdf_document.load_page(page_num)
                file_data += page.get_text()
            file_data_list.append(file_data)
        except Exception as e:
            flash(f"Error loading the document {selected_document}: {str(e)}", 'error')

    # Generate a new question ID for each question if not present in the session
    if 'question_id' not in flask_session:
        flask_session['question_id'] = str(uuid.uuid4())

    if not api_key:
        return jsonify({"status": "error", "message": "OpenAI API key not found."})

    response_text = chatbot(api_key, flask_session.get('messages', []), query_text, file_data_list)

    # Update the conversation history
    flask_session['conversation_history'].append({"role": "user", "content": query_text})
    flask_session['conversation_history'].append({"role": "assistant", "content": response_text})

    timestamp = datetime.now()
    visit_id = flask_session['visit_id']
    

    if visit_id is None or timestamp is None:
        return jsonify({"status": "error", "message": "Visit ID or timestamp not provided."})

    # Store the rating, visit_id, and timestamp in the evaluations table
    # You need to replace the following code with your database logic
    connection = create_db_connection()
    cursor = connection.cursor()

    # Assuming you have an 'evaluations' table with columns 'effectiveness_rating', 'visit_id', and 'timestamp'
    sql = "INSERT INTO evaluations (visit_id, question_id, timestamp) VALUES (%s, %s, %s)"
    cursor.execute(sql, (visit_id, str(uuid.uuid4()), timestamp))

    # Get the last inserted question_id using cursor.lastrowid
    last_inserted_id = cursor.lastrowid
    print(last_inserted_id)
    print(visit_id)

    connection.commit()
    cursor.close()
    connection.close()

    # Initialize last_inserted_id if not present in the session
    flask_session.setdefault('last_inserted_id', last_inserted_id)
    flask_session.setdefault('visit_id', visit_id)

    return jsonify({"response": response_text, "last_inserted_id": last_inserted_id, "visit_id": visit_id})



# Submit Rating
@app.route('/submit_rating', methods=['POST'])
def submit_rating():
    data = request.get_json()
    effectiveness_rating = data.get('rating')

     # Retrieve visit ID from the session
    visit_id = data.get('visit_id')
    last_inserted_id = data.get('last_inserted_id')

    # Check if either 'visit_id' or 'current_question_id' is missing
    if visit_id is None or last_inserted_id is None:
        return jsonify({"status": "error", "message": "Visit ID or current question ID not found in session."})

    # Ensure 'ratings' key is initialized in the session
    flask_session.setdefault('ratings', {})

    # Update the effectiveness rating for the specified question_id in the evaluations table
    # Replace the following code with your database logic
    connection = create_db_connection()
    cursor = connection.cursor()

    try:
        # Check if a record with the specified question_id exists and is associated with the user's session
        sql_check_existing = "SELECT COUNT(*) FROM evaluations WHERE id = %s AND visit_id = %s"
        cursor.execute(sql_check_existing, (last_inserted_id, visit_id))
        count = cursor.fetchone()[0]

        if count > 0:
            # Update the existing record
            sql_update_rating = "UPDATE evaluations SET effectiveness_rating = %s WHERE id = %s AND visit_id = %s"
            cursor.execute(sql_update_rating, (effectiveness_rating, last_inserted_id, visit_id))
            connection.commit()

            # Mark the question as rated in the session
            flask_session['ratings'][last_inserted_id] = True

            return jsonify({"status": "success"})
        else:
            # No record found for the specified question_id or not associated with the user's session
            return jsonify({"status": "error", "message": "No record found for the specified Question ID or not associated with the user's session."})

    finally:
        cursor.close()
        connection.close()


@app.route('/reset_session', methods=['POST'])
def reset_session():
    # Clear user-specific session data
    flask_session.pop('conversation_history', None)
    flask_session.pop('ratings', None)
    flask_session.pop('easeratings', None)
    flask_session.pop('question_id', None)
    flask_session.pop('last_inserted_id', None)

    # Generate a new visit_id
    new_visit_id = str(uuid.uuid4())

    # Update the visit_id in the session
    flask_session['visit_id'] = new_visit_id

    # Respond with success message or new visit_id
    return jsonify({"status": "success", "new_visit_id": new_visit_id})



@app.route('/submit_ease_of_use_rating', methods=['POST'])
def submit_ease_of_use_rating():
    data = request.get_json()
    ease_of_use_rating = data.get('ease_rating')

      # Retrieve visit ID from the session
    visit_id = data.get('visit_id')

    last_inserted_id = data.get('last_inserted_id')

      # Check if either 'visit_id' or 'current_question_id' is missing
    if visit_id is None or last_inserted_id is None:
        return jsonify({"status": "error", "message": "Visit ID or current question ID not found in session."})

    # Ensure 'ratings' key is initialized in the session
    flask_session.setdefault('easeratings', {})

    # Update the effectiveness rating for the specified question_id in the evaluations table
    # Replace the following code with your database logic
    connection = create_db_connection()
    cursor = connection.cursor()

    try:
        # Check if a record with the specified question_id exists and is associated with the user's session
        sql_check_existing = "SELECT COUNT(*) FROM evaluations WHERE id = %s AND visit_id = %s"
        cursor.execute(sql_check_existing, (last_inserted_id, visit_id))
        count = cursor.fetchone()[0]

        if count > 0:
            # Update the existing record
            sql_update_rating = "UPDATE evaluations SET ease_of_use = %s WHERE id = %s AND visit_id = %s"
            cursor.execute(sql_update_rating, (ease_of_use_rating, last_inserted_id, visit_id))
            connection.commit()

            # Mark the question as rated in the session
            flask_session['easeratings'][last_inserted_id] = True

             # Trigger session reset
            reset_session()

            return jsonify({"status": "success"})
        else:
            # No record found for the specified question_id or not associated with the user's session
            return jsonify({"status": "error", "message": "No record found for the specified Question ID or not associated with the user's session."})

    finally:
        cursor.close()
        connection.close()


# Function to send conversation history in real-time
@app.route('/get_history', methods=['GET'])
def get_history():
    # Check if 'conversation_history' is present in the session
    if 'conversation_history' not in flask_session:
        return jsonify([])  # Return an empty list if 'conversation_history' is not present

    conversation_history = flask_session['conversation_history']

    # Apply the condition to filter out user messages containing "PDF File Type"
    filtered_history = [
        {"role": message["role"], "content": message["content"]}
        for message in conversation_history
        if not (message["role"] == "user" and "PDF File Type" in message["content"])
    ]

    return jsonify(filtered_history)

@app.route('/download_transcript', methods=['GET'])
def download_transcript():
    # Check if 'messages' exists in the session
    if 'messages' not in flask_session:
        return jsonify({"status": "error", "message": "No messages found in the session."})

    # Create a PDF document
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # Iterate through the messages and add each message to the PDF
    for message in flask_session['conversation_history']:
        role, content = message["role"], message["content"]

        # Skip messages with the role "user" that contain "PDF File Type"
        if role == "user" and "PDF File Type" in content:
            continue

        # Set text color based on the role
        if role == 'user':
            pdf.set_text_color(0, 0, 255)  # Blue for user messages
        else:
            pdf.set_text_color(0, 0, 0)  # Black for assistant messages

        # Add the message content to the PDF
        pdf.multi_cell(0, 10, txt=content)

    # Save the PDF to a temporary file with a unique filename based on visit_id
    temp_filename = f"transcript_{flask_session['visit_id']}.pdf"
    pdf.output(temp_filename)

    # Send the file for download
    return send_file(temp_filename, as_attachment=True, download_name='conversation_transcript.pdf')


# Admin Section
@app.route('/admin')
def admin_panel():
    return render_template('admin_panel.html')

@app.route('/admin/upload_document', methods=['POST'])
def upload_document():
    files = request.files.getlist('file')

    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            app.config['UPLOADED_FILES'].append(file_path)

    flash('Documents uploaded successfully!', 'success')
    return render_template('admin_panel.html')


if __name__ == "__main__":
    knowledgebase_folder = "knowledgebase"
    os.makedirs(knowledgebase_folder, exist_ok=True)

    if not os.listdir(knowledgebase_folder):
        print("Knowledgebase folder is empty. Combining PDFs...")
        combine_pdfs("uploaded_documents", knowledgebase_folder)
    else:
        print("Knowledgebase folder is not empty. No need to update.")

    app.run(debug=True, host='0.0.0.0')


  
