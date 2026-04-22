# Customer Churn Prediction


## 📌 Overview

Customer churn is one of the most critical metrics for any e-commerce business. Acquiring new customers is significantly more expensive than retaining existing ones, and even small improvements in retention can lead to substantial revenue gains. This project focuses on predicting customer churn using transactional and behavioral data, enabling proactive retention strategies.

---

## ❓ Problem Statement

The goal is to predict whether a customer is likely to churn within a defined future window based on their past activity. Accurate churn prediction allows businesses to:

* Identify at-risk customers early
* Optimize marketing spend
* Improve customer lifetime value (CLV)

---

## ⚙️ Methodology

The pipeline follows a structured, end-to-end workflow:

**1. Data Extraction**

* Pulled raw transactional and user-level data from a PostgreSQL database

**2. Feature Engineering**

* Aggregated user behavior over a fixed historical window
* Created structured features (see below)

**3. Dataset Construction**

* Defined churn labels based on inactivity in a future prediction window
* Built a supervised learning dataset

**4. Modeling**

* Trained and evaluated multiple models:

  * Logistic Regression
  * Decision Tree
  * Naive Bayes
  * Random Forest
  * XGBoost
  * Voting Classifier
  * Stacking Classifier

**5. Evaluation**

* Compared models using multiple metrics (F1, AUC, training time)

---

## 📊 Data Description

* **Dataset size:** ~2,700 users

* **Time window:** ~3 months of activity

* **Granularity:** User-level aggregated features

* **Churn definition:**
  A user is considered *churned* if they show no activity in the defined future prediction window

* **Class balance:**
  Moderately imbalanced (churn vs non-churn), requiring attention during modeling

---

## 🧩 Feature Engineering

Features were grouped into meaningful behavioral categories:

### 1. RFM (Recency, Frequency, Monetary)

* Days since last purchase
* Number of transactions
* Total spend

👉 Captures overall customer value and engagement

### 2. Behavioral Features

* Session/activity frequency
* Purchase patterns
* Engagement consistency

👉 Reflects how actively users interact with the platform

### 3. Trend-Based Features

* Change in activity over time
* Increasing/decreasing engagement signals

👉 Helps detect early signs of churn

### 4. Temporal Features

* Time-based patterns (e.g., recency decay)

👉 Adds context to behavioral signals

---

## 📈 Model Performance
<img width="485" height="162" alt="image" src="https://github.com/user-attachments/assets/5258d3a2-5040-4d58-a856-6ce1d98c10ae" />

---

## 🔍 Key Findings & Limitations

### 1. Low AUC (~0.57 max)

Even the best model (Stacking) only reaches ~0.57 AUC, which is barely above random.

This suggests:

* Weak separability between churners and non-churners
* Features are not strongly predictive
* Model performance is threshold-dependent (F1 looks high, but ranking quality is poor)

---

### 2. Limited Data (2.7k users, ~3 months)

This is the biggest constraint.

* Short time horizon → incomplete churn behavior
* Limited user history → weak patterns
* Small dataset → unstable generalization

👉 Churn is inherently longitudinal, and this setup undercaptures it

---

### 3. Misleadingly High F1 Scores

Models like XGBoost (87%) and Stacking (85%) show strong F1 scores but low AUC, indicating

* Overfitting to class imbalance or threshold
* Poor probability calibration
* Weak ranking ability despite decent classification cutoff

---

### 4. Ensemble Models Barely Add Value

Despite higher complexity:

* Voting classifier underperforms (AUC 0.48)
* Stacking improves slightly but at high computational cost

This indicates limited signal in the dataset rather than model limitations

---

### 5. Weak Feature–Target Relationship

Low AUC + inconsistent model gains strongly suggest:

* Features do not capture true churn drivers
* Missing key signals (intent, satisfaction, lifecycle stage)

---

## Recommendations for Production

### 1. Extend Historical Window

* Move from 3 months → 6–12 months
* Capture repeat behavior and churn cycles

### 2. Build Stronger Temporal Features

* Rolling activity trends
* Frequency decay
* Behavioral momentum

### 3. Improve Label Definition

* Test multiple churn windows
* Consider probabilistic churn scoring

### 4. Add New Data Sources

* Marketing touchpoints
* Customer support interactions
* Product/category-level engagement

### 5. Deployment Strategy

* Use time-based validation
* Retrain quarterly
* Monitor model drift

---

## 🛠️ Tech Stack

* **Languages & Data:** Python, Pandas, NumPy
* **Database:** PostgreSQL
* **Modeling:** scikit-learn, XGBoost
* **Ensembling:** Voting & Stacking Classifiers
* **Explainability:** SHAP, LIME
* **Visualization:** Matplotlib, Seaborn
* **Version Control:** Git, GitHub
* **Automation:** GitHub Actions

---

## 📎 Future Work

* Deploy batch churn scoring pipeline
* Integrate with CRM for retention campaigns
* Build dashboards for business stakeholders
* Explore sequence models if data volume increases

---

## Plots

<img width="507" height="432" alt="download" src="https://github.com/user-attachments/assets/5dafd8d3-27cb-424c-8de4-0113fbaeef07" />

                                Confusion Matrix of the Stacking Classifier Model. As can be seen it is unable to distinguish TN values.
<img width="992" height="558" alt="download" src="https://github.com/user-attachments/assets/dcaca8f9-18d1-4cb5-9018-3ec6a1f9d7fa" />

                                SHAP Heatmap. As can be seen, most features have weak, inconsistent impact. No clear segmentation pattern across instances

---


## Project Structure
- `sql/`: Contains raw feature extraction logic.
- `src/`: Modular python scripts for data, engineering, and modeling.
- `notebooks/`: Exploratory Data Analysis and experimentation.

## Setup
1. Clone the repo.
2. Install dependencies: `pip install -r requirements.txt`.
3. Create a `.env` file with your DB credentials (`DB_HOST`, `DB_NAME`, etc.).
4. Run `python src/predict.py` to generate the latest churn risks.

 not deploy as-is; Collect more data and iterate for performance.
