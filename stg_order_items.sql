with source as (
    select * from {{ source('olist', 'order_items_dataset') }}
)
select
    order_id,
    order_item_id,
    product_id,
    seller_id,
    price as revenue,
    freight_value,
    cast(shipping_limit_date as timestamp) as shipping_limit_at
from source