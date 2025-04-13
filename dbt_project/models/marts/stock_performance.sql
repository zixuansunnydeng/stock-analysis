with daily_metrics as (
    select * from {{ ref('int_daily_stock_metrics') }}
),

stock_performance as (
    select
        date_trunc(trading_date, month) as month,

        -- Stock market indices monthly aggregations
        avg(sp500_price) as avg_sp500_price,
        avg(nasdaq_price) as avg_nasdaq_price,
        sum(nasdaq_volume) as total_nasdaq_volume,

        -- Tech stocks monthly aggregations
        avg(apple_price) as avg_apple_price,
        sum(apple_volume) as total_apple_volume,
        avg(microsoft_price) as avg_microsoft_price,
        sum(microsoft_volume) as total_microsoft_volume,
        avg(google_price) as avg_google_price,
        sum(google_volume) as total_google_volume,
        avg(nvidia_price) as avg_nvidia_price,
        sum(nvidia_volume) as total_nvidia_volume,
        avg(amazon_price) as avg_amazon_price,
        sum(amazon_volume) as total_amazon_volume,
        avg(meta_price) as avg_meta_price,
        sum(meta_volume) as total_meta_volume,
        avg(tesla_price) as avg_tesla_price,
        sum(tesla_volume) as total_tesla_volume,

        -- Commodities monthly aggregations
        avg(gold_price) as avg_gold_price,
        avg(crude_oil_price) as avg_crude_oil_price,
        avg(natural_gas_price) as avg_natural_gas_price,

        -- Cryptocurrencies monthly aggregations
        avg(bitcoin_price) as avg_bitcoin_price,
        avg(ethereum_price) as avg_ethereum_price,

        -- Average price by asset class
        avg(avg_tech_price) as avg_tech_price,
        avg(avg_commodity_price) as avg_commodity_price,
        avg(avg_crypto_price) as avg_crypto_price,

        -- Count of data points in the month
        count(*) as data_points
    from daily_metrics
    group by 1
    order by 1 desc
)

select * from stock_performance
