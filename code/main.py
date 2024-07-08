from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
from transcription import textdocs, audio
from vectordataset import inputdata, queries, weaviateutils
import json
import os

# Initialize the Flask application:
app = Flask(__name__)
CORS(app)

# Configure the Flask application to use sessions:
app.secret_key = 'secret'

# Create an empty users.json file if it doesn't exist
if not os.path.isfile('users.json'):
    with open('users.json', 'w') as file:
        json.dump({}, file)

# Create the base route:
@app.route('/')
def index():
    if 'username' in session:
        return render_template('index.html')
    else:
        return redirect(url_for('show_login'))

# Show the register form:
@app.route('/register', methods=['GET'])
def show_register():
    return render_template('login.html')

# Process the register form:
@app.route('/register', methods=['POST'])
def register():
    # Load the users from the JSON file:
    with open('users.json', 'r') as file:
        users_db = json.load(file)

    # Check if the user already exists:
    if request.form['username'] in users_db:
        return 'User already exists', 400
    else:
        users_db[request.form['username']] = {
            'password': request.form['password'],
            'role': request.form['role']
        }

        # Save the users to the JSON file:
        with open('users.json', 'w') as file:
            json.dump(users_db, file)

        return redirect(url_for('show_login'))
    

# Show the login form:
@app.route('/login', methods=['GET'])
def show_login():
    return render_template('login.html')


# Process the login form:
@app.route('/login', methods=['POST'])
def login():
    # Load the users from the JSON file:
    with open('users.json', 'r') as file:
        users_db = json.load(file)

    # Check if the user exists and the password is correct:
    if request.form['username'] in users_db and request.form['password'] == users_db[request.form['username']]['password']:
        # Store the user in the session:
        session['username'] = request.form['username']
        session['role'] = users_db[request.form['username']]['role']
        return redirect(url_for('index'))
    else:
        return 'Invalid username or password', 401
    
# Professor menu for chats:
@app.route('/professor', methods=['GET'])
def show_professor():
    if 'username' not in session:
        return 'Please log in first.', 401
    elif session['role'] != 'teacher':
        return 'You do not have permission to access this page.', 403
    else:
        return render_template('student-chat.html')

# Transcribe the document and add it to the vector dataset:
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'username' not in session:
        return 'Please log in first.', 401
    
    if 'file' not in request.files:
        return 'No file part', 400
    
    file = request.files['file']
    filename = secure_filename(file.filename)
    file_path = os.path.join('uploads', filename)
    file.save(file_path)
    transcription = process_document(filename, file_path)

    # Add the transcription to the vector dataset:
    data = inputdata.loadDataObject(filename, transcription)
    vectors = []
    for i, data_obj in enumerate(data):
        vectors.append(inputdata.get_embedding_data(data_obj))

    # Send to the vector dataset:
    weaviateutils.send_vectors(data, "LearningMaterial", vectors)

    # Associate the file with the user:
    with open('users.json', 'r') as file:
        users_db = json.load(file)

    user_data = users_db[session['username']]
    if 'files' not in user_data:
        user_data['files'] = []
    user_data['files'].append(filename)

    # Save the users to the JSON file:
    with open('users.json', 'w') as file:
        json.dump(users_db, file)

    return 'File processed correctly!', 204

# Ask the question:
@app.route('/ask', methods=['POST'])
def ask_question():
    # If conversation does not have a log file, create a unique log in chat_logs folder, with the name of the user:
    if not os.path.exists('chat_logs'):
        os.makedirs('chat_logs')
    if not os.path.exists(os.path.join('chat_logs', session['username'])):
        os.makedirs(os.path.join('chat_logs', session['username']))
    if not os.path.exists(os.path.join('chat_logs', session['username'], 'log.txt')):
        with open(os.path.join('chat_logs', session['username'], 'log.txt'), 'w') as file:
            file.write('')

    data = request.get_json()
    question = data['question']

    # Add the question to the log file:
    with open(os.path.join('chat_logs', session['username'], 'log.txt'), 'a') as file:
        file.write('Q: ' + question + '\n')

    answer = process_question(question)

    # Add the answer to the log file:
    with open(os.path.join('chat_logs', session['username'], 'log.txt'), 'a') as file:
        file.write('A: ' + answer + '\n')

    return jsonify(answer=answer)

# Get the documents of the user:
@app.route('/documents')
def documents():
    if 'username' not in session:
        return 'Please log in first.', 401

    with open('users.json', 'r') as file:
        users_db = json.load(file)

    # If the user is a teacher, return all the documents:
    if session['role'] == 'teacher':
        files = []
        for user in users_db:
            if 'files' in users_db[user]:
                files += users_db[user]['files']
        return jsonify(files=files)
    
    # If the user is a student, return only their documents:
    user_data = users_db[session['username']]

    if 'files' not in user_data:
        return jsonify(files=[])
    
    files = user_data['files']
    return jsonify(files=files)

# Get the conversations of the user:
@app.route('/conversations')
def conversations():
    if session['role'] != 'teacher':
        return 'Only teachers can access this endpoint', 401
    
    # Get all the chat logs in the chat_logs folder, in the user's folders:
    conversations = []
    for user in os.listdir('chat_logs'):
        conversations.append(user)

    return jsonify(conversations=conversations)

# Get the log of a conversation:
@app.route('/conversations/<user>')
def conversation(user):
    if session['role'] != 'teacher':
        return 'Only teachers can access this endpoint', 401
    
    # Get the log file of the conversation:
    with open(os.path.join('chat_logs', user, 'log.txt'), 'r', encoding="utf-8") as file:
        log = file.read()

    return jsonify(log=log)


# Delete the file:
@app.route('/delete-file', methods=['POST'])
def delete_file():
    data = request.get_json()
    filename = data['filename']
    
    # 1. Remove from vector database
    weaviateutils.delete_vector("LearningMaterial", filename)

    # 2. Remove from file system
    if os.path.exists(os.path.join('uploads', filename)):
        os.remove(os.path.join('uploads', filename))
    else:
        return 'File not found', 404
    
    # 3. Remove from user
    with open('users.json', 'r') as file:
        users_db = json.load(file)

    user_data = users_db[session['username']]
    if 'files' not in user_data:
        return 'File not found in user', 404
    user_data['files'].remove(filename)

    # Save the users to the JSON file:
    with open('users.json', 'w') as file:
        json.dump(users_db, file)

    return 'File deleted successfully!', 200


# Process the document:
def process_document(filename, file):
    print(f"Processing document: {file}")
    # Check if the file is one of the allowed types/extensions:
    if filename.split('.')[-1] not in ['mp3', 'wav', 'm4a', 'mp4', 'mov', 'avi', 'mkv', 'pdf', 'docx', 'doc', 'txt']:
        return 'Invalid file type', 400
    
    # Perform the transcription depending on the file type:
    if filename.split('.')[-1] in ['mp3', 'wav', 'm4a']:
        transcription = audio.transcribe_audio(file)
    elif filename.split('.')[-1] in ['mp4', 'mov', 'avi', 'mkv']:
        transcription = audio.transcribe_video(file)
    elif filename.split('.')[-1] in ['pdf']:
        transcription = textdocs.read_pdf(file)
    elif filename.split('.')[-1] in ['docx', 'doc']:
        transcription = textdocs.read_docx(file)
    else:
        transcription = textdocs.read_txt(file)

    print(transcription)
    return transcription

# Process the question:
def process_question(question):
    # Retrieve the vector values from Weaviate:
    vector_query = queries.get_embedding_query(question)
    results = weaviateutils.get_vector_values("LearningMaterial", vector_query)
    if len(results) == 0:
        return "Sorry, I don't know the answer to that question."
    else:
        return queries.answer_question_database(results, question)

# Run the application:
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')