import pandas as pd
import numpy as np
from database import fetch_data
from feature_engineering import clean_data
from models import get_stacking_model
from sklearn.preprocessing import StandardScaler
from imblearn.over_sampling import SMOTE
import os

def run_pipeline():
    print("--- Starting Churn Prediction Pipeline ---")
    
    # 1. Data Acquisition
    print("Fetching data from database...")
    df_raw = fetch_data()
    
    # 2. Cleaning and Feature Engineering
    print("Engineering features...")
    df_cleaned = clean_data(df_raw)
    
    # Separate IDs and Target for processing
    customer_ids = df_cleaned['customer_id']
    X = df_cleaned.drop(['customer_id', 'churn_label'], axis=1)
    # Ensure all categorical variables from training are present (One-Hot Encoding)
    X = pd.get_dummies(X)
    
    y = df_cleaned['churn_label']
    
    # 3. Preprocessing (Standardization & Resampling)
    # Note: In a production environment, you would usually load a saved scaler object here.
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # 4. Model Initialization & Training
    # Based on the notebook, the Stacking Classifier is our champion model.
    print("Training Stacking Classifier...")
    model = get_stacking_model()
    
    # Handling class imbalance with SMOTE before fitting
    sm = SMOTE(random_state=42)
    X_res, y_res = sm.fit_resample(X_scaled, y)
    
    model.fit(X_res, y_res)
    
    # 5. Generate Predictions
    print("Generating risk scores...")
    probs = model.predict_proba(X_scaled)[:, 1]
    predictions = model.predict(X_scaled)
    
    # 6. Export Results
    output = pd.DataFrame({
        'customer_id': customer_ids,
        'churn_probability': probs,
        'is_high_risk': predictions
    })
    
    # Sort by highest risk first
    output = output.sort_values(by='churn_probability', ascending=False)
    
    output_path = 'output/predictions/churn_results_latest.csv'
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    output.to_csv(output_path, index=False)
    
    print(f"Success! Predictions saved to {output_path}")

if __name__ == "__main__":
    run_pipeline()
