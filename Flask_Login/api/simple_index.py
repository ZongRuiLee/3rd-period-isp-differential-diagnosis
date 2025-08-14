from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import os
import json
import datetime

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Mock disease prediction for demo purposes
MOCK_DISEASES = [
    "Common Cold", "Influenza", "Migraine", "Tension Headache", 
    "Seasonal Allergies", "Gastroenteritis", "Urinary Tract Infection",
    "Bronchitis", "Pneumonia", "Appendicitis", "Gallstones", "Kidney Stones"
]

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Simple mock authentication (replace with proper auth)
        if username and password:
            session['username'] = username
            return redirect(url_for('home'))
        return "Invalid credentials", 401
    
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm = request.form['confirmpassword']

        if password != confirm:
            return "Passwords don't match", 400

        if username and password:
            session['username'] = username
            return redirect(url_for('home'))
        
        return "Invalid input", 400

    return render_template('signup.html')

@app.route('/home', methods=['GET', 'POST'])
def home():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    if request.method == "POST":
        symptoms = []
        i = 1
        while f'symptom{i}' in request.form:
            symptoms.append(request.form[f'symptom{i}'])
            i += 1
        
        if symptoms:
            # Mock prediction based on symptom count
            import random
            predicted_disease = random.choice(MOCK_DISEASES)
            
            # Store in session (replace with database in production)
            if 'disease_history' not in session:
                session['disease_history'] = []
            
            session['disease_history'].append({
                'disease': predicted_disease,
                'date': datetime.datetime.now().strftime("%m/%d/%Y")
            })
            
            return render_template(f"{predicted_disease}.html")
    
    return render_template('homepage.html')

@app.route('/disease_history')
def history():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    disease_history = session.get('disease_history', [])
    return render_template('disease_history.html', disease_history=disease_history)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/health')
def health():
    return jsonify({"status": "healthy", "message": "Flask app is running on Vercel!"})

# Vercel handler
def handler(request, context):
    return app(request, context)

if __name__ == '__main__':
    app.run(debug=True) 