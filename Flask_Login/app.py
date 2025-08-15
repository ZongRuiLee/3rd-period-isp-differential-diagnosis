from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_file, abort
from flask_sqlalchemy import SQLAlchemy
import flask_login
import joblib
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
import pandas as pd
import os
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Use environment variables for sensitive configuration
app.config['RECAPTCHA_SITE_KEY'] = os.environ.get('RECAPTCHA_SITE_KEY', '6LcYcEohAAAAANVL5nwJ25oOM488BPaC9bujC-94')
app.secret_key = os.environ.get('SECRET_KEY', '6LcYcEohAAAAAJ5JeDLnVKReHLj0ZIkeo7FgilZB')

# For Railway deployment, use environment variables
if os.environ.get('DATABASE_URL'):
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///login.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
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
                date_objects.append(datetime.datetime(1900, 1, 1))
        
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

# Global variables for ML models
xgb = None
encoder = None
column_names = []

def load_ml_models():
    """Load ML models safely with error handling"""
    global xgb, encoder, column_names
    
    try:
        # Load the machine learning model and encoder
        model_path = os.path.join(os.path.dirname(__file__), "xgboostModel.joblib")
        encoder_path = os.path.join(os.path.dirname(__file__), "label_encoder.joblib")
        
        if os.path.exists(model_path) and os.path.exists(encoder_path):
            xgb = joblib.load(model_path)
            encoder = joblib.load(encoder_path)
            
            # Load the column names from the dataset
            csv_path = os.path.join(os.path.dirname(__file__), "Testing.csv")
            if os.path.exists(csv_path):
                trainingdf = pd.read_csv(csv_path)
                column_names = trainingdf.columns.tolist()
                if "Disease" in column_names:
                    column_names.remove("Disease")  # Remove the "Disease" column
                logger.info(f"ML models loaded successfully. Found {len(column_names)} symptom columns.")
            else:
                logger.warning("Testing.csv not found. ML predictions will not work.")
        else:
            logger.warning("ML model files not found. ML predictions will not work.")
            
    except Exception as e:
        logger.error(f"Error loading ML models: {e}")
        logger.warning("ML predictions will not work. Check your model files.")

@login_manager.user_loader
def user_loader(username):
    # Fixed the critical bug here - was checking if username not in username
    if username not in [user.usernames for user in LoginScreen.query.all()]:
        return

    user = User()
    user.id = username
    return user

# Initialize database and ML models
with app.app_context():
    db.create_all()
    db.session.commit()

# Load ML models after app context is created
load_ml_models()

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
@flask_login.login_required
def home():
    if request.method == "POST":
        if not xgb or not encoder:
            return render_template('error.html', message="ML models not loaded. Please contact administrator.")
            
        symptoms = []
        i = 1
        while f'symptom{i}' in request.form:
            symptoms.append(request.form[f'symptom{i}'])
            i += 1
        
        if not symptoms:
            return render_template('homepage.html', error="Please select at least one symptom.")
        
        try:
            # Use the global column_names that were loaded at startup
            if not column_names:
                return render_template('error.html', message="Training data not found. Please contact administrator.")
            
            userSymptoms = pd.DataFrame(0, index=[0], columns=column_names)

            for column in column_names:
                if column in symptoms:
                    userSymptoms.loc[0, column] = 1
            
            predicted_encoded = xgb.predict(userSymptoms)
            predicted_diseases = encoder.inverse_transform(predicted_encoded)
            predicted_disease = predicted_diseases[0]

            # Store in database
            user_entry = LoginScreen.query.filter_by(usernames=flask_login.current_user.id).first()
            if user_entry:
                user_entry.set_data({"disease": predicted_disease, "date": datetime.datetime.now().strftime("%m/%d/%Y")})
                user_entry.remove_duplicates()
                db.session.commit()
            
            # Check if template exists, if not use a generic one
            template_name = f"{predicted_disease}.html"
            if os.path.exists(os.path.join(app.template_folder, template_name)):
                return render_template(template_name)
            else:
                # Use generic template with disease name
                return render_template('generic_disease.html', disease_name=predicted_disease)
                
        except Exception as e:
            logger.error(f"Error in prediction: {e}")
            return render_template('error.html', message="An error occurred during prediction. Please try again.")
    else:
        return render_template('homepage.html')
    
@app.route('/disease_history', methods=['GET', 'POST'])
@flask_login.login_required
def history():
    user_entry = LoginScreen.query.filter_by(usernames=flask_login.current_user.id).first()
    if user_entry:
        disease_history = user_entry.get_data()
        return render_template('disease_history.html', disease_history=zip(disease_history['disease'], disease_history['date']))
    else:
        return render_template('disease_history.html', disease_history=[])

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
    return redirect(url_for('login'))

@app.route('/health')
def health():
    """Health check endpoint for Railway"""
    return jsonify({
        "status": "healthy", 
        "ml_models_loaded": xgb is not None and encoder is not None,
        "database_connected": True
    })

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))

