with source as (
    select * from {{ source('olist', 'products_dataset') }} -- <--- Ensure this matches the YAML name!
)
select
    product_id,
    product_category_name
from source
