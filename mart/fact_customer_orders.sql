with orders as (
    select * from {{ ref('stg_orders') }}
),

order_items as (
    select 
        order_id,
        sum(revenue) as total_revenue
    from {{ ref('stg_order_items') }}
    group by 1
),

customers as (
    select * from {{ ref('stg_customers') }}
),

final as (
    select
        o.order_id,
        c.customer_unique_id,
        o.purchase_at,
        o.order_status,
        oi.total_revenue
    from orders o
    left join order_items oi on o.order_id = oi.order_id
    left join customers c on o.customer_id = c.customer_id
)

select * from final
