############## PROCSTOP BACKEND ###################################################################################################################################################################
# -*- coding: utf-8 -*-
# Local imports
import random
from datetime import timedelta
import os

# Third party imports
from flask import Flask, render_template, redirect, request, url_for, session, jsonify, flash
from flask_pymongo import PyMongo
from flask_bcrypt import Bcrypt
from flask import flash
from bson import ObjectId
from dotenv import load_dotenv
from pymongo import MongoClient
import pymongo

TF_ENABLE_ONEDNN_OPTS=0

# Project imports
from chatbot import Chatbot
from feature_extraction import feature_extraction
from settings import *
 
load_dotenv()
# Flask app configuration
app = Flask(__name__)

uri = os.getenv("MONGO_URI")
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")
app.config["API_KEY"] = os.getenv("API_KEY")
app.config['SESSION_PERMANENT'] = True
app.permanent_session_lifetime = timedelta(minutes=60)

# Database configuration
# mongo = PyMongo(app)
client = MongoClient(uri,server_api=pymongo.server_api.ServerApi(version="1", strict=True, deprecation_errors=True) )
db = client['procstop']

bcrypt = Bcrypt(app)

# Chatbot initialization
procstop = Chatbot(api_key=app.config["API_KEY"], language = 'ES', model = "gpt-4", db = db)

def hash_password(password):
    """
    Encrypt the password to user's privacy and security

    Args:
        password (str): User's password

    Return:
        encrypted_password (str): Encrypted user's password
    """
    return bcrypt.generate_password_hash(password).decode('utf-8')

@app.route('/')
def welcome():
    """
    Route to welcome page
    """
    return render_template('welcome.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Login backend to verify user's identity
    """
    if request.method == 'POST':
        session.permanent = True
        if 'login_attempts' not in session:
            session['login_attempts'] = 0

        # Login form definition
        username = request.form.get('username')
        password = request.form.get('password')
 
        # User verification
        user = db.users.find_one({'username': username})
        if user and bcrypt.check_password_hash(user['password'], password):
            session['username'] = username
            session['user_id'] = str(user['_id'])
            procstop.user_id = str(user['_id'])
            session.pop('login_attempts', None)
            procstop.start_conver()
            return redirect(url_for('chatbot'))
        else:
            session['login_attempts'] += 1
            if session['login_attempts'] > 5:
                flash('Has alcanzado el número máximo de intentos de inicio de sesion. Intentalo de nuevo mas tarde.', 'danger')
                return render_template('login.html'), 429
            else:
                flash('Usuario o contraseña incorrectos.', 'danger')
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """
    Signup backend to register a new user veryfing username and email are not in use.
    """
    if request.method == 'POST':
        # Signup form definition
        fullname = request.form.get('fullname')
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        age = request.form.get('age')
        gender = request.form.get('gender')
        country = request.form.get('country')
        language = request.form.get('language')

        form_data = {'fullname': fullname, 'username': username, 'email': email}
        
        # Email not used verification
        if db.users.find_one({'email': email}):
            flash('Este correo electrónico ya está registrado.', 'error')
            return render_template('signup.html', error="Este correo electrónico ya está registrado.", form_data=form_data)
        
         # Username not used verification
        existing_user = db.users.find_one({'username': username})
        if existing_user:
            flash('El nombre de usuario ya está en uso.', 'error')
            return render_template('signup.html', error="Usuario ya existe", form_data=form_data)
        
        # Password confirmation
        if password != confirm_password:
            flash('Las contraseñas no coinciden.', 'error')
            return render_template('signup.html', error="Las contraseñas no coinciden", form_data=form_data)

        # Password hassing
        hashed_password = hash_password(password)

        # User registration in mongo
        db.users.insert_one({
            'fullname': fullname, 
            'email': email, 
            'username': username, 
            'password': hashed_password,
            'age': age,
            'gender': gender,
            'country': country,
            'language': language
        })
        
      # Login redirection
        flash('Registro exitoso. Por favor, inicie sesión.', 'success')
        return redirect(url_for('login'))
    return render_template('signup.html', form_data={})

@app.route('/chatbot')
def chatbot():
    """
    Chatbot initialization with user login verification
    """
    # User login verification
    if 'username' not in session:
        return redirect(url_for('login'))
    
    # Welcoming message
    welcoming_msgs = [
        "Hola, ¿cómo te sientes hoy? Estoy aquí para ayudarte.",
        "¡Bienvenido! Me gustaría saber cómo estás, ¿quieres hablar de ello?",
        "¡Buenas! ¿Cómo te encuentras?",
        "¿Qué tal? Me interesa saber cómo te sientes hoy, ¿hay algo en particular que quieras compartir?",
        "Hola, ¿hay algo que te preocupe hoy o quieras discutir? Estoy aquí para escucharte.",
        "¡Hola! Si te apetece hablar, me gustaría saber cómo has estado últimamente.",
        "Bienvenido, ¿qué tal va el día? Estoy aquí para hablarlo si quieres.",
        "Hola, ¿qué tal tu día hasta ahora? Me interesa escuchar lo que tienes en mente.",
        "¡Saludos! ¿Te gustaría compartir cómo te sientes hoy? Estoy aquí para apoyarte.",
        "Hola, estoy aquí para escucharte. ¿Quieres hablar sobre cómo ha sido tu semana?"
        ]
    welcoming_msg = random.choice(welcoming_msgs)
    
    return render_template('chatbot.html', welcoming_msg = welcoming_msg)

@app.route("/chat", methods=["POST"])
def chat():
    """
    Chatbot backend to get responses and analyze user's input messages
    """
    # User definition
    username = session.get('username')
    if procstop.user_id is None:
        procstop.user_id = username

    # Input message form
    user_message = request.json.get("message")
    if not user_message:
        return jsonify({"error": "No message provided"}), 400

    # Input message processing
    features_dict = feature_extraction(user_message)

    # Update conversation context
    procstop.update_context(features_dict)

    # Response message from procstop with exceptions
    try:
        response = procstop.get_response(user_message)
    except TimeoutError:
        return jsonify({"error": "The chatbot service is temporarily unavailable. Please try again later."}), 503
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "An unexpected error occurred: " + str(e)}), 500

    # Save conversation data to mongo
    update_result = procstop.save_conver(db, user_message, response, features_dict)
    return jsonify({"reply": response, "update_status": update_result.modified_count})

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    """
    Settings backend for updating user data 
    """
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']

    if request.method == 'POST':
        # Form definition
        name = request.form.get('name')
        username = request.form.get('username')
        language = request.form.get('language')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        # Duplicated username verification
        existing_user = db.users.find_one({'username': username, '_id': {'$ne': ObjectId(user_id)}})
        if existing_user:
            flash('El nombre de usuario ya está en uso. Elige otro.', 'danger')
            return redirect(url_for('settings'))

        # Password confirmation
        if password and password != confirm_password:
            flash('Las contraseñas no coinciden. Inténtalo de nuevo.', 'danger')
            return redirect(url_for('settings'))

        # Data update
        update_data = {
            'fullname': name,
            'username': username,
            'language': language
        }

        # Password update
        if password:
            hashed_password = hash_password(password)
            update_data['password'] = hashed_password

        # User data update in mongo
        db.users.update_one({'_id': ObjectId(user_id)}, {'$set': update_data})

        flash('Cambios actualizados con éxito.', 'success')
        return redirect(url_for('settings'))

    # Get old user settings
    user_settings = get_user_settings(db, user_id)
    return render_template('settings.html', settings=user_settings)

@app.route('/delete_data', methods=['POST'])
def delete_data():
    """
    Backend for deleting user's data, including setings and conversations
    """
    # User login verification
    if 'user_id' not in session:
        return redirect(url_for('login'))

    # User definition
    user_id = session['user_id']

    # Data deletion
    db.conversations.delete_many({'user_id': user_id})
    db.settings.delete_one({'user_id': user_id})
    flash('Todos tus datos han sido borrados.', 'success')

    return redirect(url_for('settings'))

@app.route('/delete_account', methods=['POST'])
def delete_account():
    """
    Backend for deleting user's account
    """
    # User login verification
    if 'user_id' not in session:
        return redirect(url_for('login'))

    # User definition
    user_id = session['user_id']

    # Account deletion
    db.users.delete_one({"_id": user_id})
    session.clear()

    return redirect(url_for('welcome'))

@app.route('/logout', methods=['GET'])
def logout():
    """
    Logout backend
    """
    # User logout
    session.clear() 
    return redirect(url_for('login'))

@app.route('/analytics')
def analytics():
    """
    Backend for user's data analysis
    """
    # User login verification
    if 'user_id' not in session:
        return redirect(url_for('login'))

    # User definition
    user_id = session['user_id']

    
    try:
        emotion_labels, emotion_data, hobby_labels, hobby_data = procstop.get_user_data(user_id)
        return render_template('analytics.html', 
                               emotion_labels=emotion_labels, 
                               emotion_data=emotion_data,
                               hobby_labels=hobby_labels, 
                               hobby_data=hobby_data)
    except Exception as e:
        return str(e)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
