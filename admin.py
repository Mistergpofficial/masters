from flask import Flask, render_template, request, flash
from flask_admin import Admin, BaseView, expose
from flask_admin.contrib.fileadmin import FileAdmin
from werkzeug.utils import secure_filename
import os
import secrets

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploaded_documents'
app.config['ALLOWED_EXTENSIONS'] = {'pdf'}

admin = Admin()

# Create upload folder if it doesn't exist
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Initialize session state
app.config['UPLOADED_FILES'] = []

# Check if the file has a valid extension
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Admin Section
class MyAdminView(BaseView):
    @expose('/')
    def index(self):
        return self.render('index.html')

    @expose('/upload_document', methods=['POST'])
    def upload_document(self):
        files = request.files.getlist('file')

        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                app.config['UPLOADED_FILES'].append(file_path)

        flash('Documents uploaded successfully!', 'success')
        return self.render('admin.html')

admin = Admin(app, name='MyAdmin', template_mode='bootstrap3')
admin.add_view(MyAdminView(name='Upload Document'))

if __name__ == '__main__':
    strong_secret_key = secrets.token_hex(32)
    app.secret_key = strong_secret_key

    app.run(debug=True)

    
