-- Monthly sales and profit trend across categories
SELECT
    d.year,
    d.month,
    p.category,
    ROUND(SUM(f.sales), 2) AS total_sales,
    ROUND(SUM(f.profit), 2) AS total_profit,
    SUM(f.quantity) AS total_quantity
FROM fact_sales f
JOIN dim_date d ON f.order_date = d.order_date
JOIN dim_product p ON f.product_id = p.product_id
GROUP BY d.year, d.month, p.category
ORDER BY d.year, d.month, total_sales DESC;

-- Regional sales and margin performance
SELECT
    r.region,
    r.state,
    COUNT(DISTINCT f.order_id) AS order_count,
    ROUND(SUM(f.sales), 2) AS total_sales,
    ROUND(SUM(f.profit), 2) AS total_profit
FROM fact_sales f
JOIN dim_region r ON f.region_id = r.region_id
GROUP BY r.region, r.state
ORDER BY total_sales DESC;

-- Top 10 products by profit
SELECT
    p.product_id,
    p.product_name,
    p.category,
    p.sub_category,
    ROUND(SUM(f.sales), 2) AS total_sales,
    ROUND(SUM(f.profit), 2) AS total_profit
FROM fact_sales f
JOIN dim_product p ON f.product_id = p.product_id
GROUP BY p.product_id, p.product_name, p.category, p.sub_category
ORDER BY total_profit DESC
LIMIT 10;

-- Customer segment contribution
SELECT
    c.segment,
    COUNT(DISTINCT c.customer_id) AS unique_customers,
    ROUND(SUM(f.sales), 2) AS total_sales,
    ROUND(AVG(f.discount) * 100, 2) AS avg_discount_pct
FROM fact_sales f
JOIN dim_customer c ON f.customer_id = c.customer_id
GROUP BY c.segment
ORDER BY total_sales DESC;
