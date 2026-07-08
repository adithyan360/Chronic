import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import classification_report, accuracy_score
import pickle
import os

# Create models directory if it doesn't exist
os.makedirs('models', exist_ok=True)

def generate_synthetic_data(disease, n_samples=1000):
    """Generate synthetic medical data for training"""
    np.random.seed(42)
    
    # Base demographics
    data = {
        'age': np.random.normal(65, 15, n_samples).clip(18, 100),
        'gender': np.random.choice([0, 1], n_samples),  # 0=Female, 1=Male
        'duration_years': np.random.exponential(5, n_samples).clip(0, 50),
        'medications_count': np.random.poisson(3, n_samples).clip(0, 10),
        'compliance': np.random.beta(8, 2, n_samples),  # Skewed towards higher compliance
        'exercise_hours': np.random.gamma(2, 2, n_samples).clip(0, 20),
        'diet_quality': np.random.normal(6, 2, n_samples).clip(1, 10),
        'stress_level': np.random.normal(5, 2, n_samples).clip(1, 10),
        'sleep_hours': np.random.normal(7, 1.5, n_samples).clip(1, 12),
        'smoking_status': np.random.choice([0, 1], n_samples, p=[0.8, 0.2]),  # 0=Non-smoker, 1=Smoker
        'hypertension': np.random.choice([0, 1], n_samples, p=[0.6, 0.4]),
        'diabetes': np.random.choice([0, 1], n_samples, p=[0.7, 0.3]),
        'obesity': np.random.choice([0, 1], n_samples, p=[0.65, 0.35])
    }
    
    # Add exactly 6 biomarker features for all diseases (standardized)
    data.update({
        'biomarker_1': np.random.normal(100, 20, n_samples).clip(50, 200),
        'biomarker_2': np.random.normal(80, 15, n_samples).clip(40, 150),
        'biomarker_3': np.random.normal(60, 10, n_samples).clip(30, 120),
        'biomarker_4': np.random.normal(40, 8, n_samples).clip(20, 80),
        'biomarker_5': np.random.normal(30, 5, n_samples).clip(10, 60),
        'biomarker_6': np.random.normal(20, 3, n_samples).clip(5, 40)
    })
    
    df = pd.DataFrame(data)
    
    # Generate target variables based on features
    # Current stage (0-3)
    severity_score = (
        df['age'] * 0.02 +
        df['duration_years'] * 0.15 +
        (1 - df['compliance']) * 3 +
        df['medications_count'] * 0.1 +
        df['stress_level'] * 0.1 +
        df['smoking_status'] * 0.5 +
        df['hypertension'] * 0.3 +
        df['diabetes'] * 0.3 +
        np.random.normal(0, 0.5, n_samples)
    )
    
    df['current_stage'] = pd.cut(severity_score, bins=4, labels=[0, 1, 2, 3]).astype(int)
    
    # Progression (0=stable, 1=next_stage, 2=advanced)
    progression_risk = severity_score + np.random.normal(0, 0.3, n_samples)
    df['progression_12months'] = pd.cut(progression_risk, 
                                       bins=[-np.inf, 2, 4, np.inf], 
                                       labels=[0, 1, 2]).astype(int)
    
    # Complications (binary for each complication type)
    complication_risk = severity_score + np.random.normal(0, 0.5, n_samples)
    df['complication_1'] = (complication_risk > 3).astype(int)
    df['complication_2'] = (complication_risk > 2.5).astype(int)
    df['complication_3'] = (complication_risk > 3.5).astype(int)
    
    return df

def train_models_for_disease(disease):
    """Train all models for a specific disease"""
    print(f"\nTraining models for {disease}...")
    
    # Generate synthetic data
    df = generate_synthetic_data(disease, n_samples=2000)
    
    # Prepare features
    feature_cols = [col for col in df.columns if not col.startswith(('current_stage', 'progression', 'complication'))]
    X = df[feature_cols]
    
    # Normalize features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Save scaler
    scaler_path = f'models/{disease.lower().replace(" ", "_")}_scaler.pkl'
    with open(scaler_path, 'wb') as f:
        pickle.dump(scaler, f)
    
    # Train severity model
    y_severity = df['current_stage']
    X_train, X_test, y_train, y_test = train_test_split(X_scaled, y_severity, test_size=0.2, random_state=42)
    
    severity_model = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)
    severity_model.fit(X_train, y_train)
    severity_accuracy = accuracy_score(y_test, severity_model.predict(X_test))
    
    severity_path = f'models/{disease.lower().replace(" ", "_")}_severity.pkl'
    with open(severity_path, 'wb') as f:
        pickle.dump(severity_model, f)
    
    print(f"Severity Model Accuracy: {severity_accuracy:.3f}")
    
    # Train progression model
    y_progression = df['progression_12months']
    X_train, X_test, y_train, y_test = train_test_split(X_scaled, y_progression, test_size=0.2, random_state=42)
    
    progression_model = GradientBoostingClassifier(n_estimators=100, max_depth=6, random_state=42)
    progression_model.fit(X_train, y_train)
    progression_accuracy = accuracy_score(y_test, progression_model.predict(X_test))
    
    progression_path = f'models/{disease.lower().replace(" ", "_")}_progression.pkl'
    with open(progression_path, 'wb') as f:
        pickle.dump(progression_model, f)
    
    print(f"Progression Model Accuracy: {progression_accuracy:.3f}")
    
    # Train complications model (multi-label)
    y_complications = df[['complication_1', 'complication_2', 'complication_3']]
    X_train, X_test, y_train, y_test = train_test_split(X_scaled, y_complications, test_size=0.2, random_state=42)
    
    complications_model = RandomForestClassifier(n_estimators=100, max_depth=8, random_state=42)
    # For simplicity, we'll predict the sum of complications
    y_train_sum = y_train.sum(axis=1)
    y_test_sum = y_test.sum(axis=1)
    
    complications_model.fit(X_train, y_train_sum)
    complications_accuracy = accuracy_score(y_test_sum, complications_model.predict(X_test))
    
    complications_path = f'models/{disease.lower().replace(" ", "_")}_complications.pkl'
    with open(complications_path, 'wb') as f:
        pickle.dump(complications_model, f)
    
    print(f"Complications Model Accuracy: {complications_accuracy:.3f}")
    
    return {
        'severity_accuracy': severity_accuracy,
        'progression_accuracy': progression_accuracy,
        'complications_accuracy': complications_accuracy
    }

def main():
    """Train models for all diseases"""
    diseases = ['Heart Disease', 'Type 2 Diabetes', 'Chronic Kidney Disease']
    
    print("Starting ProgressionPred Model Training...")
    print("=" * 50)
    
    results = {}
    for disease in diseases:
        results[disease] = train_models_for_disease(disease)
    
    print("\n" + "=" * 50)
    print("TRAINING SUMMARY")
    print("=" * 50)
    
    for disease, metrics in results.items():
        print(f"\n{disease}:")
        print(f"  Severity Model:      {metrics['severity_accuracy']:.3f}")
        print(f"  Progression Model:   {metrics['progression_accuracy']:.3f}")
        print(f"  Complications Model: {metrics['complications_accuracy']:.3f}")
    
    print(f"\nAll models trained and saved to 'models/' directory!")
    print(f"Total files created: {len(diseases) * 4} model files")

if __name__ == "__main__":
    main()