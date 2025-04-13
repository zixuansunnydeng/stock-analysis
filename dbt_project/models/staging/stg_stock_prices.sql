with source as (
    select * from {{ source('raw', 'stock_market_raw') }}
),

renamed as (
    select
        -- Convert date string to date type
        SAFE_CAST(date AS STRING) as date_str,
        PARSE_DATE('%Y-%m-%d', SAFE_CAST(date AS STRING)) as trading_date,

        -- Stock market indices
        SandP_500_Price as sp500_price,
        Nasdaq_100_Price as nasdaq_price,
        Nasdaq_100_Vol_ as nasdaq_volume,

        -- Tech stocks
        Apple_Price as apple_price,
        Apple_Vol_ as apple_volume,
        Tesla_Price as tesla_price,
        Tesla_Vol_ as tesla_volume,
        Microsoft_Price as microsoft_price,
        Microsoft_Vol_ as microsoft_volume,
        Google_Price as google_price,
        Google_Vol_ as google_volume,
        Nvidia_Price as nvidia_price,
        Nvidia_Vol_ as nvidia_volume,
        Amazon_Price as amazon_price,
        Amazon_Vol_ as amazon_volume,
        Meta_Price as meta_price,
        Meta_Vol_ as meta_volume,
        Netflix_Price as netflix_price,
        Netflix_Vol_ as netflix_volume,

        -- Commodities
        Gold_Price as gold_price,
        Gold_Vol_ as gold_volume,
        Natural_Gas_Price as natural_gas_price,
        Natural_Gas_Vol_ as natural_gas_volume,
        Crude_oil_Price as crude_oil_price,
        Crude_oil_Vol_ as crude_oil_volume,
        Silver_Price as silver_price,
        Silver_Vol_ as silver_volume,
        Copper_Price as copper_price,
        Copper_Vol_ as copper_volume,
        Platinum_Price as platinum_price,
        Platinum_Vol_ as platinum_volume,

        -- Cryptocurrencies
        Bitcoin_Price as bitcoin_price,
        Bitcoin_Vol_ as bitcoin_volume,
        Ethereum_Price as ethereum_price,
        Ethereum_Vol_ as ethereum_volume,

        -- Other
        Berkshire_Price as berkshire_price,
        Berkshire_Vol_ as berkshire_volume,

        -- Add metadata
        row_id,
        current_timestamp() as _loaded_at
    from source
)

select * from renamed
