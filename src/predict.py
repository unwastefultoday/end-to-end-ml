import pandas as pd
from database import fetch_data
from feature_engineering import clean_data
from models import get_stacking_model, save_model, load_pretrained_model
from sklearn.preprocessing import StandardScaler
from imblearn.over_sampling import SMOTE
import os
import gspread
from google.oauth2.service_account import Credentials
import json

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
    #scaler = StandardScaler()
    #X_scaled = scaler.fit_transform(X)

    # 2. Model Selection (Pretrained vs Retrain)
    model = None
    if not force_retrain:
        print("Attempting to load pretrained model...")
        model = load_pretrained_model('model/stacking_21_04.pkl')
    
    if model is None:
        if not force_retrain:
            print("Pretrained model not found. Proceeding to train...")
        else:
            print("Force retrain requested. Training new model...")
            
        model = get_stacking_model()
        sm = SMOTE(random_state=42)
        X_res, y_res = sm.fit_resample(X, y)
        model.fit(X_res, y_res)
        
        # Save the newly trained model for next time
        save_model(model, 'models/stacking_21_04.pkl')
    else:
        print("Successfully loaded pretrained model.")

    # 3. Generate Results
    probs = model.predict_proba(X)[:, 1]
    predictions = model.predict(X)
    
    output = pd.DataFrame({
        'customer_id': customer_ids,
        'churn_probability': probs,
        'is_high_risk': predictions
    }).sort_values(by='churn_probability', ascending=False)
    
    output_path = 'output/predictions/churn_results_latest.csv'
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    output.to_csv(output_path, index=False)
    print(f"Results saved to {output_path}")
    return output

def push_to_sheets(df, spreadsheet_name="Churn Predictions", sheet_index=0):
    print(f"Pushing results to Google Sheet: {spreadsheet_name}...")
    try:
        creds_json = os.environ.get("GOOGLE_CREDS")
        
        if not creds_json:
            # Fallback for local development if the env var isn't set
            if os.path.exists('credentials.json'):
                gc = gspread.service_account(filename='credentials.json')
            else:
                raise EnvironmentError("GOOGLE_CREDS environment variable not found.")
        else:
            creds_dict = json.loads(creds_json)
            scopes = [
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive"
            ]
            creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
            gc = gspread.authorize(creds)

        sh = gc.open(spreadsheet_name)
        worksheet = sh.get_worksheet(sheet_index)
        worksheet.clear()
        set_with_dataframe(worksheet, df)

        print(f"Successfully pushed {len(df)} rows to '{spreadsheet_name}'.")
    except Exception as e:
        print(f"Critical Error during Google Sheets sync: {e}")
if __name__ == "__main__":

    print("Running Pipeline")
    output=run_pipeline()
    push_to_sheets(output)
    print("Pushed results to Google Sheets")
