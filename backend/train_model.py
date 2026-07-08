import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
import pickle
import os

def generate_synthetic_data(num_samples=1000):
    np.random.seed(42)
    
    # Generate random features
    revenue = np.random.uniform(10, 1000, num_samples)  # 10L to 10Cr
    profit_margin = np.random.uniform(-0.1, 0.4, num_samples)
    debt_ratio = np.random.uniform(0.1, 1.5, num_samples)
    cash_flow = np.random.uniform(-50, 200, num_samples)
    credit_score = np.random.uniform(300, 900, num_samples)
    collateral_value = np.random.uniform(0, 500, num_samples)
    gst_growth = np.random.uniform(-0.2, 0.5, num_samples)
    
    data = pd.DataFrame({
        'revenue': revenue,
        'profit_margin': profit_margin,
        'debt_ratio': debt_ratio,
        'cash_flow': cash_flow,
        'credit_score': credit_score,
        'collateral_value': collateral_value,
        'gst_growth': gst_growth
    })
    
    # Rule-based target generation for realistic synthetic data
    # 0 = Approve, 1 = Review, 2 = Reject
    def decide(row):
        score = 0
        if row['credit_score'] > 750: score += 3
        elif row['credit_score'] > 600: score += 1
        else: score -= 2
        
        if row['debt_ratio'] < 0.4: score += 2
        elif row['debt_ratio'] < 0.8: score += 0
        else: score -= 2
        
        if row['profit_margin'] > 0.15: score += 2
        elif row['profit_margin'] > 0.05: score += 1
        else: score -= 1
        
        if row['cash_flow'] > 50: score += 1
        
        if score >= 4: return 0  # Approve
        if score >= 1: return 1  # Review
        return 2  # Reject

    data['loan_status'] = data.apply(decide, axis=1)
    return data

def train_and_save_model():
    print("Generating synthetic dataset...")
    df = generate_synthetic_data()
    
    # Save training data
    os.makedirs('data', exist_ok=True)
    df.to_csv('data/training_dataset.csv', index=False)
    
    X = df.drop('loan_status', axis=1)
    y = df['loan_status']
    
    print("Training Random Forest model...")
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X, y)
    
    # Save model
    os.makedirs('models', exist_ok=True)
    with open('models/credit_model.pkl', 'wb') as f:
        pickle.dump(model, f)
    
    print("Model trained and saved to models/credit_model.pkl")

if __name__ == "__main__":
    train_and_save_model()
