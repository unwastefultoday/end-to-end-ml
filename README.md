# Customer Churn Prediction

An end-to-end ML pipeline to predict customer churn using behavioral and transactional data.

## Project Structure
- `sql/`: Contains raw feature extraction logic.
- `src/`: Modular python scripts for data, engineering, and modeling.
- `notebooks/`: Exploratory Data Analysis and experimentation.

## Setup
1. Clone the repo.
2. Install dependencies: `pip install -r requirements.txt`.
3. Create a `.env` file with your DB credentials (`DB_HOST`, `DB_NAME`, etc.).
4. Run `python src/predict.py` to generate the latest churn risks.

## Model Performance
The stacking classifier shows over 35% increase in F1 Score from the baseline model and yet is unable to outperform random on this scale as AUC is 57%. 

## Recommendation:
do not deploy as-is; Collect more data and iterate for performance.
