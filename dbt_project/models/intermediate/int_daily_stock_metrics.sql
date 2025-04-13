with stock_prices as (
    select * from {{ ref('stg_stock_prices') }}
),

daily_metrics as (
    select
        trading_date,

        -- Stock market indices
        sp500_price,
        nasdaq_price,
        nasdaq_volume,

        -- Tech stocks
        apple_price,
        apple_volume,
        tesla_price,
        tesla_volume,
        microsoft_price,
        microsoft_volume,
        google_price,
        google_volume,
        nvidia_price,
        nvidia_volume,
        amazon_price,
        amazon_volume,
        meta_price,
        meta_volume,
        netflix_price,
        netflix_volume,

        -- Commodities
        gold_price,
        gold_volume,
        natural_gas_price,
        natural_gas_volume,
        crude_oil_price,
        crude_oil_volume,
        silver_price,
        silver_volume,
        copper_price,
        copper_volume,
        platinum_price,
        platinum_volume,

        -- Cryptocurrencies
        bitcoin_price,
        bitcoin_volume,
        ethereum_price,
        ethereum_volume,

        -- Other
        berkshire_price,
        berkshire_volume,

        -- Calculate tech stock average price
        (apple_price + microsoft_price + google_price + amazon_price + meta_price + netflix_price + nvidia_price + tesla_price) / 8 as avg_tech_price,

        -- Calculate commodity average price
        (gold_price + silver_price + copper_price + platinum_price) / 4 as avg_commodity_price,

        -- Calculate crypto average price
        (bitcoin_price + ethereum_price) / 2 as avg_crypto_price,

        -- Add metadata
        row_id,
        _loaded_at
    from stock_prices
)

select * from daily_metrics
