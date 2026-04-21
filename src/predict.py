import pandas as pd
from database import fetch_data
from feature_engineering import clean_data
from models import get_stacking_model, save_model, load_pretrained_model
from sklearn.preprocessing import StandardScaler
from imblearn.over_sampling import SMOTE
import os

def run_pipeline(force_retrain=False):
    print("--- Churn Prediction Pipeline ---")
    
    # 1. Fetch and Clean Data
    df_raw = fetch_data()
    df_cleaned = clean_data(df_raw)
    
    customer_ids = df_cleaned['customer_id']
    X = df_cleaned.drop(['customer_id', 'churn_label'], axis=1)
    X = pd.get_dummies(X)
    y = df_cleaned['churn_label']
    
    # Preprocessing
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # 2. Model Selection (Pretrained vs Retrain)
    model = None
    if not force_retrain:
        print("Attempting to load pretrained model...")
        model = load_pretrained_model('models/stacking_21_04.pkl')
    
    if model is None:
        if not force_retrain:
            print("Pretrained model not found. Proceeding to train...")
        else:
            print("Force retrain requested. Training new model...")
            
        model = get_stacking_model()
        sm = SMOTE(random_state=42)
        X_res, y_res = sm.fit_resample(X_scaled, y)
        model.fit(X_res, y_res)
        
        # Save the newly trained model for next time
        save_model(model, 'models/stacking_21_04.pkl')
    else:
        print("Successfully loaded pretrained model.")

    # 3. Generate Results
    probs = model.predict_proba(X_scaled)[:, 1]
    predictions = model.predict(X_scaled)
    
    output = pd.DataFrame({
        'customer_id': customer_ids,
        'churn_probability': probs,
        'is_high_risk': predictions
    }).sort_values(by='churn_probability', ascending=False)
    
    output_path = 'output/predictions/churn_results_latest.csv'
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    output.to_csv(output_path, index=False)
    print(f"Results saved to {output_path}")

if __name__ == "__main__":
    # Change to True if you want to ignore the pickle and retrain
    run_pipeline(force_retrain=False)
