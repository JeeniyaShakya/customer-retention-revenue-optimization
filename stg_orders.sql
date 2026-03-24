with source as (
    select * from {{ source('olist', 'orders_dataset') }}
)
select
    order_id,
    customer_id,
    order_status,
    cast(order_purchase_timestamp as timestamp) as purchase_at,
    cast(order_delivered_customer_date as timestamp) as delivered_at
from source