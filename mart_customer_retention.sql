with fact_orders as (
    select * from {{ ref('fact_customer_orders') }}
),

customer_metrics as (
    select
        customer_unique_id,
        order_id,
        purchase_at,
        total_revenue,
        -- Get the date of the very first purchase for this customer
        min(purchase_at) over(partition by customer_unique_id) as first_purchase_at,
        -- Get the date of the previous purchase to calculate "days between"
        lag(purchase_at) over(partition by customer_unique_id order by purchase_at) as previous_purchase_at,
        -- Count which order number this is for the customer (1st, 2nd, 3rd...)
        row_number() over(partition by customer_unique_id order by purchase_at) as order_sequence
    from fact_orders
)

select
    *,
    case 
        when order_sequence = 1 then 'New' 
        else 'Repeat' 
    end as customer_type,
    timestamp_diff(purchase_at, previous_purchase_at, DAY) as days_since_last_purchase
from customer_metrics