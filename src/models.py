from xgboost import XGBClassifier
from sklearn.ensemble import StackingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

def get_stacking_model():
    estimators = [
        ('lr', make_pipeline(StandardScaler(), LogisticRegression(class_weight='balanced'))),
        ('rf', RandomForestClassifier(class_weight='balanced')),
        ('xgb', XGBClassifier(eval_metric='logloss'))
    ]
    
    stk = StackingClassifier(
        estimators=estimators,
        final_estimator=RandomForestClassifier(class_weight='balanced')
    )
    return stk
