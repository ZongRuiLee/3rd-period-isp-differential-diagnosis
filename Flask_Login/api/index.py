from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
import flask_login
import joblib
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
import pandas as pd
import os
import json
from vercel import Vercel

app = Flask(__name__)
app.config['RECAPTCHA_S8ITE_KEY'] = '6LcYcEohAAAAANVL5nwJ25oOM488BPaC9bujC-94'
app.secret_key = '6LcYcEohAAAAAJ5JeDLnVKReHLj0ZIkeo7FgilZB'

# For Vercel, we'll use environment variables for database
if os.environ.get('VERCEL_ENV'):
    # Use PostgreSQL on Vercel (you'll need to set up a database)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///login.db')
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///login.db'

db = SQLAlchemy(app)

login_manager = flask_login.LoginManager()
login_manager.init_app(app)

class LoginScreen(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usernames = db.Column(db.String(100), unique=True, nullable=False)
    passwords = db.Column(db.String(200), nullable=False)
    disease_history = db.Column(db.Text, default=json.dumps({'disease': [], 'date': []}))

    def set_data(self, data):
        current_data = self.get_data()
        
        # Add the new disease and date at the beginning
        current_data['disease'].insert(0, data['disease'])
        current_data['date'].insert(0, data['date'])
        
        # Convert string dates to datetime objects for sorting
        date_objects = []
        for date_str in current_data['date']:
            try:
                # Parse the MM/DD/YYYY format
                date_obj = datetime.datetime.strptime(date_str, "%m/%d/%Y")
                date_objects.append(date_obj)
            except ValueError:
                # If parsing fails, use a very old date
                date_obj = datetime.datetime(1900, 1, 1)
                date_objects.append(date_obj)
        
        # Sort diseases and dates based on dates (most recent first)
        sorted_indices = sorted(range(len(date_objects)), key=lambda i: date_objects[i], reverse=True)
        
        sorted_diseases = [current_data['disease'][i] for i in sorted_indices]
        sorted_dates = [current_data['date'][i] for i in sorted_indices]
        
        # Update the data with sorted lists
        current_data['disease'] = sorted_diseases
        current_data['date'] = sorted_dates
        
        self.disease_history = json.dumps(current_data)

    def get_data(self):
        return json.loads(self.disease_history)
    
    def remove_duplicates(self):
        current_data = self.get_data()

        # Use a set to track unique (disease, date) pairs while maintaining order
        seen = set()
        unique_diseases = []
        unique_dates = []

        for disease, date in zip(current_data['disease'], current_data['date']):
            if (disease, date) not in seen:
                seen.add((disease, date))
                unique_diseases.append(disease)
                unique_dates.append(date)

        # Update the stored disease history
        self.disease_history = json.dumps({'disease': unique_diseases, 'date': unique_dates})

class User(flask_login.UserMixin):
    pass

# Load the machine learning model and encoder
model_path = os.path.join(os.path.dirname(__file__), "..", "xgboostModel.joblib")
encoder_path = os.path.join(os.path.dirname(__file__), "..", "label_encoder.joblib")

# Check if files exist before loading
if os.path.exists(model_path) and os.path.exists(encoder_path):
    xgb = joblib.load(model_path)
    encoder = joblib.load(encoder_path)
else:
    # For Vercel deployment, you might need to handle this differently
    xgb = None
    encoder = None

# Load the column names from the dataset
csv_path = os.path.join(os.path.dirname(__file__), "..", "Testing.csv")
if os.path.exists(csv_path):
    trainingdf = pd.read_csv(csv_path)
    column_names = trainingdf.columns.tolist()
    if "Disease" in column_names:
        column_names.remove("Disease")  # Remove the "Disease" column
else:
    column_names = []

@login_manager.user_loader
def user_loader(username):
    if username not in username:
        return

    user = User()
    user.id = username
    return user

# Initialize database
with app.app_context():
    db.create_all()
    db.session.commit()

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user_entry = LoginScreen.query.filter_by(usernames=username).first()

        if user_entry and check_password_hash(user_entry.passwords, password):
            user = User()
            user.id = username
            flask_login.login_user(user)
            return redirect(url_for('home'))
        return render_template('wrongCredentials.html')
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm = request.form['confirmpassword']

        if password != confirm:
            return render_template('confirmPassword.html')

        if LoginScreen.query.filter_by(usernames=username).first():
            return render_template('existingUser.html')

        hashed_pw = generate_password_hash(password)
        new_user = LoginScreen(usernames=username, passwords=hashed_pw)

        db.session.add(new_user)
        db.session.commit()

        user = User()
        user.id = username
        flask_login.login_user(user)
        return redirect(url_for('home'))

    return render_template('signup.html')

@app.route('/home', methods=['GET', 'POST'])
def home():
    if request.method == "POST":
        if not xgb or not encoder:
            return "Model not loaded", 500
            
        symptoms = []
        i = 1
        while f'symptom{i}' in request.form:
            symptoms.append(request.form[f'symptom{i}'])
            i += 1
        
        # Construct the correct path for Testing.csv
        csv_path = os.path.join(os.path.dirname(__file__), "..", "Testing.csv")
        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"CSV file not found at {csv_path}")
        
        trainingdf = pd.read_csv(csv_path)
        column_names = trainingdf.columns.tolist()
        userSymptoms = pd.DataFrame(0, index=[0], columns=column_names)
        userSymptoms.drop(columns=["Disease"], inplace=True)

        for column in column_names:
            if column in symptoms:
                userSymptoms.loc[0, column] = 1
        
        predicted_encoded = xgb.predict(userSymptoms)
        predicted_diseases = encoder.inverse_transform(predicted_encoded)

        user_entry = LoginScreen.query.filter_by(usernames=flask_login.current_user.id).first()

        if user_entry:
            user_entry.set_data({"disease": predicted_diseases[0], "date": datetime.datetime.now().strftime("%m/%d/%Y")})
            user_entry.remove_duplicates()
            db.session.commit()
            
        return render_template(f"{predicted_diseases[0]}.html")
    else:
        return render_template('homepage.html')
    
@app.route('/disease_history', methods=['GET', 'POST'])
def history():
    user_entry = LoginScreen.query.filter_by(usernames=flask_login.current_user.id).first()
    disease_history = user_entry.get_data()

    return render_template('disease_history.html', disease_history=zip(disease_history['disease'], disease_history['date']))

@app.route('/add_disease', methods=['POST'])
@flask_login.login_required
def add_disease():
    # Get the data from the request
    data = request.json
    
    # Get the current user
    user_entry = LoginScreen.query.filter_by(usernames=flask_login.current_user.id).first()
    
    if user_entry:
        # Add the disease to the user's history
        user_entry.set_data(data)
        user_entry.remove_duplicates()
        db.session.commit()
        return jsonify({"status": "success"})
    
    return jsonify({"status": "error", "message": "User not found"}), 404

@app.route('/logout')
def logout():
    flask_login.logout_user()
    return 'Logged out'

# Vercel handler
def handler(request, context):
    return app(request, context)

# For local development
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True) 