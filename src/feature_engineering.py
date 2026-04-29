import pandas as pd
import numpy as np

def clean_data(df):
    # Handle Missing Values
    ratio_cols = ["view_to_cart_rate", "cart_to_checkout_rate", "payment_failure_rate", "return_order_rate", "refund_rate"]
    for col in ratio_cols:
        if col in df.columns:
            df[col] = df[col].fillna(0)

    recency_cols = ["recency_days", "recency_session"]
    for col in recency_cols:
        if col in df.columns:
            df[col] = df[col].fillna(df[col].max())

    time_cols = ["customer_age_days", "avg_order_gap", "avg_session_duration"]
    for col in time_cols:
        if col in df.columns:
            df[col] = df[col].fillna(df[col].median())

    # Drop Redundant/Highly Correlated Columns identified in notebook
    to_drop = ['total_items_purchased', 'has_return_history', 'returned_orders', 
               'brand_diversity', 'failed_payments', 'category_diversity', 'refund_rate']
    #df = df.drop(columns=[c for c in to_drop if c in df.columns], errors='ignore')
    df= df[['customer_id', 'acquisition_channel', 'country', 'is_email_verified',
       'marketing_opt_in', 'customer_age_days', 'total_orders',
       'total_revenue', 'avg_order_value', 'coupon_usage_count',
       'recency_days', 'avg_order_gap', 'total_sessions',
       'avg_session_duration', 'recency_session', 'product_views',
       'add_to_cart', 'checkouts', 'unique_products_viewed', 'search_count',
       'view_to_cart_rate', 'cart_to_checkout_rate', 'product_variety',
       'payment_failure_rate', 'total_refunds', 'return_order_rate',
       'device_types_used', 'churn_label', 'view_to_cart_rate_missing',
       'cart_to_checkout_rate_missing', 'recency_session_missing',
       'avg_order_gap_missing']]
    # Encoding
    df = pd.get_dummies(df, columns=['acquisition_channel', 'country'], drop_first=True)
    return df
