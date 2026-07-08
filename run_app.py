#!/usr/bin/env python3
"""
ProgressionPred Application Runner
Trains models and starts the Flask web application
"""

import os
import sys
import subprocess
import time

def check_models_exist():
    """Check if trained models exist"""
    models_dir = 'models'
    if not os.path.exists(models_dir):
        return False
    
    required_models = [
        'heart_disease_severity.pkl',
        'heart_disease_progression.pkl', 
        'heart_disease_complications.pkl',
        'type_2_diabetes_severity.pkl',
        'type_2_diabetes_progression.pkl',
        'type_2_diabetes_complications.pkl',
        'chronic_kidney_disease_severity.pkl',
        'chronic_kidney_disease_progression.pkl',
        'chronic_kidney_disease_complications.pkl'
    ]
    
    existing_models = os.listdir(models_dir)
    return all(model in existing_models for model in required_models)

def train_models():
    """Train machine learning models"""
    print("🔄 Training machine learning models...")
    print("This may take a few minutes...")
    
    try:
        result = subprocess.run([sys.executable, 'train_progression_models.py'], 
                              capture_output=True, text=True, check=True)
        print(result.stdout)
        print("✅ Models trained successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error training models: {e}")
        print(f"Error output: {e.stderr}")
        return False

def start_flask_app():
    """Start the Flask application"""
    print("\n🚀 Starting ProgressionPred web application...")
    print("📱 Open your browser and go to: http://localhost:5000")
    print("⏹️  Press Ctrl+C to stop the server")
    
    try:
        subprocess.run([sys.executable, 'app.py'], check=True)
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error starting Flask app: {e}")

def main():
    """Main application runner"""
    print("=" * 60)
    print("🏥 PROGRESSIONPRED: CHRONIC DISEASE PROGRESSION TRACKER")
    print("=" * 60)
    
    # Check if models exist
    if not check_models_exist():
        print("📊 Machine learning models not found.")
        print("🔄 Training models with synthetic data...")
        
        if not train_models():
            print("❌ Failed to train models. Exiting...")
            sys.exit(1)
    else:
        print("✅ Machine learning models found!")
    
    # Start Flask application
    start_flask_app()

if __name__ == "__main__":
    main()