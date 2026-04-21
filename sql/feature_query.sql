WITH max_date AS (
    SELECT MAX(created_at) AS max_order_date
    FROM ecom.orders
),

cutoff AS (
    SELECT 
        (DATE_TRUNC('month', max_order_date) - INTERVAL '1 month') - INTERVAL '1 day' AS cutoff_date,
        max_order_date
    FROM max_date
),

-- Only customers with at least 1 paid order before cutoff
eligible_customers AS (
    SELECT DISTINCT o.customer_id
    FROM ecom.orders o
    CROSS JOIN cutoff c
    WHERE o.payment_status = 'paid'
      AND o.created_at <= c.cutoff_date
),

base_customers AS (
    SELECT
        c.customer_id,
        c.acquisition_channel,
        c.country,
        c.created_at AS customer_created_at,
        c.is_email_verified,
        c.marketing_opt_in
    FROM ecom.customers c
    INNER JOIN eligible_customers ec
        ON c.customer_id = ec.customer_id
    CROSS JOIN cutoff cu
    WHERE c.created_at <= cu.cutoff_date
),

orders_agg AS (
    SELECT
        o.customer_id,
        COUNT(*) FILTER (WHERE o.payment_status = 'paid') AS total_orders,
        SUM(o.total) FILTER (WHERE o.payment_status = 'paid') AS total_revenue,
        AVG(o.total) FILTER (WHERE o.payment_status = 'paid') AS avg_order_value,
        MAX(o.created_at) FILTER (WHERE o.payment_status = 'paid') AS last_order_date,
        MIN(o.created_at) FILTER (WHERE o.payment_status = 'paid') AS first_order_date,
        COUNT(*) FILTER (WHERE o.applied_coupon_id IS NOT NULL) AS coupon_usage_count
    FROM ecom.orders o
    CROSS JOIN cutoff c
    WHERE o.created_at <= c.cutoff_date
    GROUP BY o.customer_id
),

order_items_agg AS (
    SELECT
        o.customer_id,
        COUNT(DISTINCT oi.variant_id) AS product_variety,
        SUM(oi.qty) AS total_items_purchased
    FROM ecom.orders o
    JOIN ecom.order_items oi ON o.order_id = oi.order_id
    CROSS JOIN cutoff c
    WHERE o.created_at <= c.cutoff_date
      AND o.payment_status = 'paid'
    GROUP BY o.customer_id
),

product_diversity AS (
    SELECT
        o.customer_id,
        COUNT(DISTINCT p.category_id) AS category_diversity,
        COUNT(DISTINCT p.brand_id) AS brand_diversity
    FROM ecom.orders o
    JOIN ecom.order_items oi ON o.order_id = oi.order_id
    JOIN ecom.product_variants pv ON oi.variant_id = pv.variant_id
    JOIN ecom.products p ON pv.product_id = p.product_id
    CROSS JOIN cutoff c
    WHERE o.created_at <= c.cutoff_date
      AND o.payment_status = 'paid'
    GROUP BY o.customer_id
),

sessions_agg AS (
    SELECT
        s.customer_id,
        COUNT(*) AS total_sessions,
        MAX(s.started_at) AS last_session_date,
        AVG(EXTRACT(EPOCH FROM (s.ended_at - s.started_at))) AS avg_session_duration
    FROM ecom.sessions s
    CROSS JOIN cutoff c
    WHERE s.started_at <= c.cutoff_date
    GROUP BY s.customer_id
),

event_agg AS (
    SELECT
        e.customer_id,
        COUNT(*) FILTER (WHERE e.event_type = 'product_view') AS product_views,
        COUNT(*) FILTER (WHERE e.event_type = 'add_to_cart') AS add_to_cart,
        COUNT(*) FILTER (WHERE e.event_type = 'begin_checkout') AS checkouts,
        COUNT(DISTINCT e.product_id) AS unique_products_viewed,
        COUNT(*) FILTER (WHERE e.event_type = 'search') AS search_count
    FROM ecom.session_events e
    CROSS JOIN cutoff c
    WHERE e.event_time <= c.cutoff_date
    GROUP BY e.customer_id
),

payment_failures AS (
    SELECT
        o.customer_id,
        COUNT(*) FILTER (WHERE o.payment_status = 'failed') AS failed_payments,
        COUNT(*) AS total_payment_attempts
    FROM ecom.orders o
    CROSS JOIN cutoff c
    WHERE o.created_at <= c.cutoff_date
    GROUP BY o.customer_id
),

refunds_agg AS (
    SELECT
        o.customer_id,
        SUM(r.amount) AS total_refunds,
        COUNT(DISTINCT r.order_id) AS returned_orders
    FROM ecom.refunds r
    JOIN ecom.orders o ON r.order_id = o.order_id
    CROSS JOIN cutoff c
    WHERE o.created_at <= c.cutoff_date
    GROUP BY o.customer_id
),

device_usage AS (
    SELECT
        s.customer_id,
        COUNT(DISTINCT d.device_type) AS device_types_used
    FROM ecom.sessions s
    JOIN ecom.devices d ON s.device_id = d.device_id
    CROSS JOIN cutoff c
    WHERE s.started_at <= c.cutoff_date
    GROUP BY s.customer_id
),

future_orders AS (
    SELECT
        o.customer_id,
        COUNT(*) AS orders_next_30d
    FROM ecom.orders o
    CROSS JOIN cutoff c
    WHERE o.payment_status = 'paid'
      AND o.created_at > c.cutoff_date
      AND o.created_at <= c.cutoff_date + INTERVAL '45 days'
    GROUP BY o.customer_id
)

SELECT
    bc.customer_id,
    bc.acquisition_channel,
    bc.country,
    bc.is_email_verified,
    bc.marketing_opt_in,

    DATE_PART('day', c.cutoff_date - bc.customer_created_at) AS customer_age_days,

    oa.total_orders,
    oa.total_revenue,
    oa.avg_order_value,
    oa.coupon_usage_count,

    DATE_PART('day', c.cutoff_date - oa.last_order_date) AS recency_days,

    CASE 
        WHEN oa.total_orders > 1 
        THEN DATE_PART('day', oa.last_order_date - oa.first_order_date) / (oa.total_orders - 1)
    END AS avg_order_gap,

    sa.total_sessions,
    sa.avg_session_duration,

    CASE 
        WHEN sa.last_session_date IS NOT NULL 
        THEN DATE_PART('day', c.cutoff_date - sa.last_session_date)
    END AS recency_session,

    ea.product_views,
    ea.add_to_cart,
    ea.checkouts,
    ea.unique_products_viewed,
    ea.search_count,

    ea.add_to_cart::float / NULLIF(ea.product_views, 0) AS view_to_cart_rate,
    ea.checkouts::float / NULLIF(ea.add_to_cart, 0) AS cart_to_checkout_rate,

    oi.product_variety,
    oi.total_items_purchased,

    pd.category_diversity,
    pd.brand_diversity,

    pf.failed_payments,
    pf.failed_payments::float / NULLIF(pf.total_payment_attempts, 0) AS payment_failure_rate,

    ra.total_refunds,
    ra.returned_orders,
    ra.returned_orders::float / NULLIF(oa.total_orders, 0) AS return_order_rate,
    ra.total_refunds::float / NULLIF(oa.total_revenue, 0) AS refund_rate,

    CASE
        WHEN COALESCE(ra.returned_orders, 0) > 0 THEN 1
        ELSE 0
    END AS has_return_history,

    COALESCE(du.device_types_used, 0) AS device_types_used,

    CASE
        WHEN c.cutoff_date + INTERVAL '45 days' > c.max_order_date THEN NULL
        WHEN COALESCE(fo.orders_next_30d, 0) = 0 THEN 1
        ELSE 0
    END AS churn_label

FROM base_customers bc
LEFT JOIN orders_agg oa ON bc.customer_id = oa.customer_id
LEFT JOIN order_items_agg oi ON bc.customer_id = oi.customer_id
LEFT JOIN product_diversity pd ON bc.customer_id = pd.customer_id
LEFT JOIN sessions_agg sa ON bc.customer_id = sa.customer_id
LEFT JOIN event_agg ea ON bc.customer_id = ea.customer_id
LEFT JOIN payment_failures pf ON bc.customer_id = pf.customer_id
LEFT JOIN refunds_agg ra ON bc.customer_id = ra.customer_id
LEFT JOIN device_usage du ON bc.customer_id = du.customer_id
LEFT JOIN future_orders fo ON bc.customer_id = fo.customer_id
CROSS JOIN cutoff c;
"""
