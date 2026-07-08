from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
import pickle
import numpy as np
import pandas as pd
import sqlite3
from datetime import datetime
import os
from werkzeug.utils import secure_filename

app = Flask(__name__, template_folder='app/templates', static_folder='app/static')
app.secret_key = 'progression_pred_secret_key'
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs('uploads', exist_ok=True)

# Add JSON filter for templates
import json
@app.template_filter('from_json')
def from_json_filter(s):
    try:
        return json.loads(s.replace("'", '"'))
    except:
        return {}

# Gemini AI configuration (optional)
try:
    import google.generativeai as genai
    GEMINI_API_KEY = "AIzaSyBh-ATGtmlgPxV1eR1Z6inSHUpXZZxI4MU"
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-2.5-flash')
    GEMINI_AVAILABLE = True
except:
    GEMINI_AVAILABLE = False
    model = None

# Disease configurations
DISEASES = {
    'Hypertension': {
        'biomarkers': ['blood_pressure_systolic', 'blood_pressure_diastolic', 'pulse_pressure', 'heart_rate'],
        'stages': ['Stage I - Normal', 'Stage II - Elevated', 'Stage III - High', 'Stage IV - Crisis'],
        'complications': ['Stroke', 'Heart Attack', 'Kidney Damage'],
        'icon': '🩸',
        'medications': ['ACE Inhibitors', 'Beta Blockers', 'Diuretics']
    },
    'Diabetes': {
        'biomarkers': ['glucose_fasting', 'hba1c', 'c_peptide', 'insulin_level'],
        'stages': ['Stage I - Prediabetes', 'Stage II - Early', 'Stage III - Established', 'Stage IV - Advanced'],
        'complications': ['Diabetic Retinopathy', 'Diabetic Nephropathy', 'Diabetic Neuropathy'],
        'icon': '🍯',
        'medications': ['Metformin', 'Insulin', 'GLP-1 Agonists']
    },
    'Heart Disease': {
        'biomarkers': ['blood_pressure_systolic', 'blood_pressure_diastolic', 'heart_rate', 'ejection_fraction', 'troponin_level'],
        'stages': ['Stage I - Mild', 'Stage II - Moderate', 'Stage III - Severe', 'Stage IV - End-stage'],
        'complications': ['Heart Attack', 'Arrhythmia', 'Heart Failure'],
        'icon': '❤️',
        'medications': ['Statins', 'Beta Blockers', 'ACE Inhibitors']
    },
    'Chronic Kidney Disease': {
        'biomarkers': ['creatinine', 'bun', 'gfr', 'proteinuria', 'hemoglobin'],
        'stages': ['Stage I - Normal', 'Stage II - Mild', 'Stage III - Moderate', 'Stage IV - Severe'],
        'complications': ['Kidney Failure', 'Cardiovascular Disease', 'Bone Disease'],
        'icon': '🫘',
        'medications': ['ACE Inhibitors', 'Phosphate Binders', 'EPO']
    },
    'Asthma/COPD': {
        'biomarkers': ['fev1', 'fvc', 'peak_flow', 'oxygen_saturation', 'eosinophil_count'],
        'stages': ['Stage I - Mild', 'Stage II - Moderate', 'Stage III - Severe', 'Stage IV - Very Severe'],
        'complications': ['Respiratory Failure', 'Pneumonia', 'Cor Pulmonale'],
        'icon': '🫁',
        'medications': ['Bronchodilators', 'Corticosteroids', 'LABA']
    }
}

def init_db():
    """Initialize SQLite database"""
    conn = sqlite3.connect('progression_pred.db')
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Drop and recreate predictions table to ensure correct schema
    cursor.execute('DROP TABLE IF EXISTS predictions')
    cursor.execute('''
        CREATE TABLE predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            disease TEXT,
            patient_data TEXT,
            current_stage TEXT,
            progression_forecast TEXT,
            complications TEXT,
            risk_score REAL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Insert demo user
    cursor.execute('INSERT OR IGNORE INTO users (username, password) VALUES (?, ?)', ('demo', 'demo123'))
    
    conn.commit()
    conn.close()

def load_model(disease, model_type):
    """Load trained model with correct feature count"""
    from sklearn.ensemble import RandomForestClassifier
    model = RandomForestClassifier(n_estimators=10, random_state=42)
    # Create training data with 19 features to match our input
    X_dummy = np.random.rand(100, 19)
    y_dummy = np.random.randint(0, 4, 100)
    model.fit(X_dummy, y_dummy)
    return model

def create_feature_vector(disease, features):
    """Convert form data to feature vector - fixed length for all diseases"""
    # Base features (13 common features)
    vector = [
        features.get('age', 50),
        1 if features.get('gender') == 'Male' else 0,
        features.get('duration_years', 5),
        features.get('medications_count', 2),
        features.get('compliance', 80) / 100,
        features.get('exercise_hours', 3),
        features.get('diet_quality', 5),
        features.get('stress_level', 5),
        features.get('sleep_hours', 7),
        1 if features.get('smoking_status') == 'Current' else 0,
        1 if features.get('hypertension') else 0,
        1 if features.get('diabetes') else 0,
        1 if features.get('obesity') else 0
    ]
    
    # Add exactly 6 biomarker features (pad with defaults if needed)
    biomarkers = DISEASES[disease]['biomarkers']
    for i in range(6):
        if i < len(biomarkers):
            vector.append(features.get(biomarkers[i], 100))
        else:
            vector.append(100)  # Default value for missing biomarkers
    
    return np.array(vector).reshape(1, -1)

def format_gemini_response(text):
    """Format Gemini response with proper line breaks"""
    if not text:
        return text
    
    # Replace bullet points that are on same line with line breaks
    formatted = text.replace('• ', '<br>• ')
    # Remove any extra spaces and clean up
    formatted = formatted.replace('  ', ' ').strip()
    # Ensure it starts without <br> if first bullet
    if formatted.startswith('<br>'):
        formatted = formatted[4:]
    
    return formatted

def calculate_risk_factors(features):
    """Calculate risk factor scores for visualization"""
    risk_factors = {
        'medication_compliance': max(0, 100 - features.get('compliance', 80)),
        'age_factor': max(0, (features.get('age', 50) - 40) * 2) if features.get('age', 50) > 60 else 10,
        'disease_duration': min(100, features.get('duration_years', 5) * 8),
        'lifestyle_score': max(0, (10 - features.get('diet_quality', 7)) * 8),
        'exercise_deficit': max(0, (5 - features.get('exercise_hours', 3)) * 15),
        'stress_level': features.get('stress_level', 5) * 8
    }
    return risk_factors

def predict_all_models(disease, feature_vector, features):
    """Make predictions using all models"""
    # Load models (using dummy models for demo)
    severity_model = load_model(disease, 'severity')
    progression_model = load_model(disease, 'progression')
    complications_model = load_model(disease, 'complications')
    
    # Predictions
    severity_score = severity_model.predict(feature_vector)[0]
    stage = min(severity_score, 3)  # Ensure valid stage index
    
    # Mock progression probabilities
    progression_probs = [0.6, 0.35, 0.05]  # stable, next_stage, advanced
    
    # Mock complication risks
    complication_risks = [0.08, 0.15, 0.12]  # Risk percentages
    
    # Calculate risk factors
    risk_factors = calculate_risk_factors(features)
    
    results = {
        'current_stage': DISEASES[disease]['stages'][stage],
        'stage_index': stage,
        'progression_forecast': {
            'stable': progression_probs[0],
            'to_next_stage': progression_probs[1],
            'to_advanced_stage': progression_probs[2]
        },
        'complications': dict(zip(DISEASES[disease]['complications'], complication_risks)),
        'risk_score': (stage + 1) * 2.5,
        'confidence': 0.85,
        'risk_factors': risk_factors
    }
    
    # Generate AI insights using Gemini
    if GEMINI_AVAILABLE and model:
        try:
            # AI Insights
            insights_prompt = f"""
            Patient has {disease} at {results['current_stage']} with risk score {results['risk_score']:.1f}/10.
            Progression risk: {results['progression_forecast']['to_next_stage']*100:.0f}% to next stage.
            
            Provide exactly 4 short recommendations as plain text bullet points (use • not numbers):
            • One immediate action needed
            • One lifestyle change
            • One monitoring requirement  
            • One prevention strategy
            
            No markdown formatting, no asterisks, no bold text. Keep each point under 25 words.
            """
            
            insights_response = model.generate_content(insights_prompt)
            if insights_response and insights_response.text:
                results['ai_insights'] = format_gemini_response(insights_response.text)
            else:
                results['ai_insights'] = "Focus on medication compliance and regular monitoring."
            
            # Medication Reminders
            meds = DISEASES[disease]['medications']
            reminders_prompt = f"""
            For {disease} patient taking {', '.join(meds)}, provide 4 simple medication tips as plain text bullet points (use • not numbers):
            • Best time to take medications
            • One important food interaction to avoid
            • One key side effect to watch for
            • What to do if you miss a dose
            
            No markdown formatting, no asterisks, no bold text. Keep each point under 20 words.
            """
            
            reminders_response = model.generate_content(reminders_prompt)
            if reminders_response and reminders_response.text:
                results['medication_reminders'] = format_gemini_response(reminders_response.text)
            else:
                results['medication_reminders'] = "Take medications as prescribed by your doctor."
            
        except Exception as e:
            results['ai_insights'] = f"Based on your {disease} assessment, focus on medication compliance and lifestyle changes."
            results['medication_reminders'] = "Take medications as prescribed by your doctor."
    else:
        results['ai_insights'] = f"Based on your {disease} assessment, focus on medication compliance and lifestyle changes."
        results['medication_reminders'] = "Take medications as prescribed by your doctor."
    
    return results

@app.route('/')
def home():
    if 'user_id' not in session:
        return render_template('landing.html')
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = sqlite3.connect('progression_pred.db')
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM users WHERE username = ? AND password = ?', (username, password))
        user = cursor.fetchone()
        conn.close()
        
        if user:
            session['user_id'] = user[0]
            session['username'] = username
            return redirect('/')
        else:
            flash('Invalid credentials')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

@app.route('/input')
def patient_input():
    disease = request.args.get('disease', 'Heart Disease')
    return render_template('patient_input.html', disease=disease, diseases=DISEASES)

@app.route('/predict', methods=['POST'])
def predict():
    data = request.form.to_dict()
    disease = data.get('disease', 'Heart Disease')
    
    # Convert form data to appropriate types
    features = {}
    for key, value in data.items():
        if key == 'disease':
            continue
        try:
            if key in ['gender', 'smoking_status', 'therapy_type']:
                features[key] = value
            elif key in ['hypertension', 'diabetes', 'obesity']:
                features[key] = value == 'on'
            else:
                features[key] = float(value) if '.' in str(value) else int(value)
        except (ValueError, TypeError):
            features[key] = 0
    
    # Create feature vector and make predictions
    feature_vector = create_feature_vector(disease, features)
    results = predict_all_models(disease, feature_vector, features)
    
    # Save to database
    conn = sqlite3.connect('progression_pred.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO predictions (user_id, disease, patient_data, current_stage, progression_forecast, complications, risk_score)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (session.get('user_id'), disease, str(features), results['current_stage'], str(results['progression_forecast']), str(results['complications']), results['risk_score']))
    conn.commit()
    conn.close()
    
    return render_template('results.html', disease=disease, results=results, features=features)

def get_health_response(user_message):
    """Get comprehensive health responses"""
    message_lower = user_message.lower()
    
    if any(word in message_lower for word in ['who are you', 'who r u', 'what are you', 'introduce']):
        return "I'm your AI Health Assistant for chronic disease management. I can help with diabetes, heart disease, hypertension, kidney disease, COPD, medications, diet, and exercise. Always consult your healthcare provider for personalized medical advice."
    elif any(word in message_lower for word in ['exercise', 'workout', 'physical activity', 'fitness']):
        return "Safe exercises for chronic conditions: Walking (start 10-15 min daily), Swimming (low-impact), Cycling, Yoga/stretching, Light strength training (2-3x/week). Always get doctor clearance first. Stop if you experience chest pain or severe shortness of breath."
    elif 'chronic disease' in message_lower:
        return "Chronic diseases are long-lasting conditions that can be controlled but not cured. Common types include diabetes, heart disease, hypertension, kidney disease, and COPD. They require ongoing medical care, lifestyle management, and regular monitoring."
    elif 'blood pressure' in message_lower:
        return "To manage blood pressure: Reduce sodium to less than 2300mg/day, Exercise 150 minutes/week, Maintain healthy weight, Limit alcohol, Manage stress through meditation/yoga, Get 7-9 hours sleep, Eat DASH diet. Monitor regularly and consult your doctor."
    elif 'diabetes' in message_lower and ('food' in message_lower or 'diet' in message_lower or 'eat' in message_lower):
        return "Diabetes-friendly eating: AVOID - refined sugars, white bread, sugary drinks, processed foods. CHOOSE - non-starchy vegetables, lean proteins, whole grains, healthy fats. Use plate method: 1/2 vegetables, 1/4 lean protein, 1/4 whole grains."
    elif 'medication' in message_lower:
        return "Medication management tips: Take exactly as prescribed, Use pill organizers, Set phone alarms, Never skip doses, Don't stop without doctor approval, Report side effects immediately, Keep updated medication list."
    else:
        return "I can help with questions about chronic diseases (diabetes, heart disease, hypertension, kidney disease, COPD), medications, diet, exercise, and lifestyle management. Always consult your healthcare provider for personalized medical advice."

@app.route('/chatbot', methods=['GET', 'POST'])
def chatbot():
    if 'user_id' not in session:
        return redirect('/login')
    
    if request.method == 'POST':
        user_message = request.json.get('message', '')
        
        # Try Gemini first, fallback to predefined responses
        if GEMINI_AVAILABLE and model and len(user_message.strip()) > 0:
            try:
                prompt = f"You are a medical AI assistant. Answer this health question briefly and clearly: {user_message}. Always end with 'Consult your healthcare provider for personalized advice.'"
                gemini_response = model.generate_content(prompt)
                if gemini_response and gemini_response.text:
                    bot_response = gemini_response.text
                else:
                    bot_response = get_health_response(user_message)
            except Exception as e:
                bot_response = get_health_response(user_message)
        else:
            bot_response = get_health_response(user_message)
        
        return jsonify({'response': bot_response})
    
    return render_template('chatbot.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/login')
    
    conn = sqlite3.connect('progression_pred.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT disease, current_stage, risk_score, timestamp 
        FROM predictions 
        WHERE user_id = ? 
        ORDER BY timestamp DESC 
        LIMIT 5
    ''', (session['user_id'],))
    user_data = cursor.fetchall()
    conn.close()
    
    return render_template('simple_dashboard.html', user_data=user_data, username=session.get('username'))

@app.route('/history')
def history():
    if 'user_id' not in session:
        return redirect('/login')
    
    conn = sqlite3.connect('progression_pred.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, disease, current_stage, risk_score, timestamp, patient_data, progression_forecast, complications
        FROM predictions 
        WHERE user_id = ? 
        ORDER BY timestamp DESC LIMIT 10
    ''', (session['user_id'],))
    predictions = cursor.fetchall()
    conn.close()
    return render_template('history.html', predictions=predictions)

@app.route('/prediction_details/<int:prediction_id>')
def prediction_details(prediction_id):
    if 'user_id' not in session:
        return redirect('/login')
    
    conn = sqlite3.connect('progression_pred.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM predictions 
        WHERE id = ? AND user_id = ?
    ''', (prediction_id, session['user_id']))
    prediction = cursor.fetchone()
    conn.close()
    
    if not prediction:
        return redirect('/history')
    
    return render_template('prediction_details.html', prediction=prediction)

@app.route('/export_pdf/<int:prediction_id>')
def export_pdf(prediction_id):
    if 'user_id' not in session:
        return redirect('/login')
    
    from flask import make_response
    
    conn = sqlite3.connect('progression_pred.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM predictions 
        WHERE id = ? AND user_id = ?
    ''', (prediction_id, session['user_id']))
    prediction = cursor.fetchone()
    conn.close()
    
    if not prediction:
        return redirect('/history')
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>MediTrack Pro - Health Report</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            .header {{ text-align: center; color: #007bff; }}
            .section {{ margin: 20px 0; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🏥 MediTrack Pro</h1>
            <h2>Chronic Disease Assessment Report</h2>
            <p>Generated on: {prediction[8]}</p>
        </div>
        
        <div class="section">
            <h3>Patient Information</h3>
            <p><strong>Disease:</strong> {prediction[2]}</p>
            <p><strong>Current Stage:</strong> {prediction[4]}</p>
            <p><strong>Risk Score:</strong> {prediction[7]:.1f}/10</p>
        </div>
        
        <div class="section">
            <h3>Recommendations</h3>
            <p>• Follow prescribed medication regimen</p>
            <p>• Maintain regular exercise routine</p>
            <p>• Monitor vital signs as recommended</p>
            <p>• Schedule regular follow-up appointments</p>
        </div>
        
        <div class="section">
            <p><em>⚠️ This report is for informational purposes only. Always consult your healthcare provider for medical decisions.</em></p>
        </div>
    </body>
    </html>
    """
    
    response = make_response(html_content)
    response.headers['Content-Type'] = 'text/html'
    response.headers['Content-Disposition'] = f'attachment; filename=meditrack_report_{prediction_id}.html'
    return response

@app.route('/prescription_scanner')
def prescription_scanner():
    if 'user_id' not in session:
        return redirect('/login')
    return render_template('prescription_scanner.html')

def analyze_prescription_with_gemini(image_path):
    """Analyze prescription image using Gemini Vision"""
    if not GEMINI_AVAILABLE or not model:
        return "<div class='alert alert-warning'>AI analysis not available. Please consult your pharmacist for prescription review.</div>"
    
    try:
        import PIL.Image
        
        # Load and analyze image
        image = PIL.Image.open(image_path)
        
        prompt = """
        Analyze this prescription image and extract:
        1. All medication names and dosages
        2. Instructions for each medication
        3. Any drug interactions or warnings
        4. Recommended monitoring
        
        If this is not a prescription image or text is unclear, say "Unable to read prescription clearly. Please upload a clearer image."
        
        Format response as HTML with proper headings and bullet points.
        """
        
        response = model.generate_content([prompt, image])
        
        if response and response.text:
            # Check if it's actually a prescription
            if "unable to read" in response.text.lower() or "not a prescription" in response.text.lower():
                return "<div class='alert alert-warning'>Unable to read prescription clearly. Please upload a clearer image of a prescription.</div>"
            else:
                return f"<h6>📋 AI Prescription Analysis:</h6>{response.text}"
        else:
            return "<div class='alert alert-danger'>Error analyzing prescription. Please try again.</div>"
            
    except Exception as e:
        return f"<div class='alert alert-danger'>Error processing image: Please upload a clear prescription image.</div>"

@app.route('/upload_prescription', methods=['POST'])
def upload_prescription():
    if 'prescription' not in request.files:
        return jsonify({'error': 'No file uploaded'})
    
    file = request.files['prescription']
    if file.filename == '':
        return jsonify({'error': 'No file selected'})
    
    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Analyze prescription using Gemini Vision
        analysis = analyze_prescription_with_gemini(filepath)
        
        return jsonify({'message': analysis, 'filename': filename})

@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect('/login')
    
    conn = sqlite3.connect('progression_pred.db')
    cursor = conn.cursor()
    
    # Get user info
    cursor.execute('SELECT username, created_at FROM users WHERE id = ?', (session['user_id'],))
    user_info = cursor.fetchone()
    
    # Get prediction stats
    cursor.execute('SELECT COUNT(*), AVG(risk_score) FROM predictions WHERE user_id = ?', (session['user_id'],))
    stats = cursor.fetchone()
    total_predictions = stats[0] or 0
    avg_risk = stats[1] or 0
    
    # Get disease distribution
    cursor.execute('SELECT disease, COUNT(*) FROM predictions WHERE user_id = ? GROUP BY disease', (session['user_id'],))
    disease_stats = cursor.fetchall()
    
    conn.close()
    
    return render_template('profile.html', 
                         user_info=user_info, 
                         total_predictions=total_predictions,
                         avg_risk=avg_risk,
                         disease_stats=disease_stats)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = sqlite3.connect('progression_pred.db')
        cursor = conn.cursor()
        try:
            cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
            conn.commit()
            flash('Account created successfully! Please login.')
            return redirect('/login')
        except sqlite3.IntegrityError:
            flash('Username already exists')
        finally:
            conn.close()
    
    return render_template('signup.html')

if __name__ == '__main__':
    init_db()
    app.run(debug=True)