with source as (
    select * from {{ source('olist', 'customers_dataset') }}
)
select
    customer_id,        -- The ID for a single session/order
    customer_unique_id, -- The permanent ID for the actual person
    customer_city,
    customer_state
from source