import pickle
import os
from xgboost import XGBClassifier
from sklearn.ensemble import StackingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

modelname = "model.pkl" # name of new model

def get_stacking_model():
    # Mirroring your notebook's full experimental setup
    estimators = [
        ('lr', make_pipeline(StandardScaler(), LogisticRegression(class_weight='balanced'))),
        ('dtc', DecisionTreeClassifier(class_weight='balanced')),
        ('nb', GaussianNB()),
        ('rf', RandomForestClassifier(class_weight='balanced')),
        ('xgb', XGBClassifier(eval_metric='logloss'))
    ]
    
    return StackingClassifier(
        estimators=estimators,
        final_estimator=RandomForestClassifier(class_weight='balanced'),
        passthrough=False
    )

def save_model(model, filepath=f'model/{modelname}'):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'wb') as f:
        pickle.dump(model, f)
    print(f"Model saved to {filepath}")

def load_pretrained_model(filepath='models/stacking_21_04.pkl'):
    if os.path.exists(filepath):
        with open(filepath, 'rb') as f:
            return pickle.load(f)
    return None
