import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from google.cloud import bigquery
import scipy.optimize as sco
import io
import base64
import warnings

# Suppress warnings
warnings.filterwarnings('ignore')

# Set up the HTML file with dashboard styling
html_content = """
<!DOCTYPE html>
<html>
<head>
    <title>Stock Market Analysis Dashboard</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #f8f9fa;
            color: #343a40;
            padding-top: 20px;
        }}
        .dashboard-header {{
            background-color: #343a40;
            color: white;
            padding: 20px 0;
            margin-bottom: 30px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }}
        .chart-container {{
            background-color: white;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            margin-bottom: 30px;
            padding: 20px;
            transition: transform 0.3s ease;
        }}
        .chart-container:hover {{
            transform: translateY(-5px);
        }}
        .chart-title {{
            font-size: 20px;
            font-weight: 600;
            margin-bottom: 15px;
            color: #343a40;
            border-bottom: 2px solid #f8f9fa;
            padding-bottom: 10px;
        }}
        .section-header {{
            background-color: #e9ecef;
            padding: 15px;
            margin: 30px 0 20px 0;
            border-radius: 8px;
            font-weight: 600;
            color: #495057;
        }}
        .nav-pills .nav-link.active {{
            background-color: #343a40;
        }}
        .tab-content {{
            padding-top: 20px;
        }}
        .dashboard-footer {{
            text-align: center;
            margin-top: 30px;
            padding: 20px 0;
            background-color: #343a40;
            color: white;
            border-radius: 10px;
        }}
        .static-img {{
            max-width: 100%;
            height: auto;
            display: block;
            margin: 0 auto;
        }}
        .metrics-card {{
            background-color: #343a40;
            color: white;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 20px;
            text-align: center;
        }}
        .metrics-value {{
            font-size: 24px;
            font-weight: bold;
        }}
        .metrics-label {{
            font-size: 14px;
            opacity: 0.8;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="dashboard-header text-center">
            <h1>Stock Market Analysis Dashboard</h1>
            <p class="lead">Comprehensive analysis of stock market data from 2019-2024</p>
        </div>

        <!-- Navigation Tabs -->
        <ul class="nav nav-pills mb-3 justify-content-center" id="pills-tab" role="tablist">
            <li class="nav-item" role="presentation">
                <button class="nav-link active" id="pills-overview-tab" data-bs-toggle="pill"
                        data-bs-target="#pills-overview" type="button" role="tab"
                        aria-controls="pills-overview" aria-selected="true">Market Overview</button>
            </li>
            <li class="nav-item" role="presentation">
                <button class="nav-link" id="pills-risk-tab" data-bs-toggle="pill"
                        data-bs-target="#pills-risk" type="button" role="tab"
                        aria-controls="pills-risk" aria-selected="false">Risk & Returns</button>
            </li>
            <li class="nav-item" role="presentation">
                <button class="nav-link" id="pills-trends-tab" data-bs-toggle="pill"
                        data-bs-target="#pills-trends" type="button" role="tab"
                        aria-controls="pills-trends" aria-selected="false">Market Trends</button>
            </li>
            <li class="nav-item" role="presentation">
                <button class="nav-link" id="pills-portfolio-tab" data-bs-toggle="pill"
                        data-bs-target="#pills-portfolio" type="button" role="tab"
                        aria-controls="pills-portfolio" aria-selected="false">Portfolio Optimization</button>
            </li>
        </ul>

        <!-- Tab Content -->
        <div class="tab-content" id="pills-tabContent">
            <!-- Market Overview Tab -->
            <div class="tab-pane fade show active" id="pills-overview" role="tabpanel" aria-labelledby="pills-overview-tab">
                <div class="section-header">
                    <h3>Market Performance</h3>
                </div>

                {market_overview_graphs}
            </div>

            <!-- Risk & Returns Tab -->
            <div class="tab-pane fade" id="pills-risk" role="tabpanel" aria-labelledby="pills-risk-tab">
                <div class="section-header">
                    <h3>Risk and Returns Analysis</h3>
                </div>

                {risk_returns_graphs}
            </div>

            <!-- Market Trends Tab -->
            <div class="tab-pane fade" id="pills-trends" role="tabpanel" aria-labelledby="pills-trends-tab">
                <div class="section-header">
                    <h3>Market Trends Analysis</h3>
                </div>

                {market_trends_graphs}
            </div>

            <!-- Portfolio Optimization Tab -->
            <div class="tab-pane fade" id="pills-portfolio" role="tabpanel" aria-labelledby="pills-portfolio-tab">
                <div class="section-header">
                    <h3>Portfolio Optimization</h3>
                </div>

                {portfolio_optimization_graphs}
            </div>
        </div>

        <div class="dashboard-footer">
            <p>Stock Market Analysis Dashboard | Created with Python, Plotly, and Matplotlib</p>
        </div>
    </div>
</body>
</html>
"""

# Load data from BigQuery
def load_data():
    PROJECT_ID = "satellite-data-pipeline-2024"  # Replace with your actual project ID
    try:
        client = bigquery.Client(project=PROJECT_ID)

        # Query monthly performance data
        monthly_performance_query = """
        SELECT
          month,
          avg_sp500_price,
          avg_nasdaq_price,
          avg_tech_price,
          avg_commodity_price,
          avg_crypto_price
        FROM
          `stock_market_data_marts.stock_performance`
        ORDER BY
          month ASC
        """
        monthly_performance = client.query(monthly_performance_query).to_dataframe()

        # Query tech stock performance data
        tech_stocks_query = """
        SELECT
          month,
          avg_apple_price,
          avg_microsoft_price,
          avg_google_price,
          avg_amazon_price,
          avg_meta_price,
          avg_nvidia_price,
          avg_tesla_price
        FROM
          `stock_market_data_marts.stock_performance`
        ORDER BY
          month ASC
        """
        tech_stocks = client.query(tech_stocks_query).to_dataframe()

        # Query commodity and crypto performance data
        commodities_crypto_query = """
        SELECT
          month,
          avg_gold_price,
          avg_crude_oil_price,
          avg_natural_gas_price,
          avg_bitcoin_price,
          avg_ethereum_price
        FROM
          `stock_market_data_marts.stock_performance`
        ORDER BY
          month ASC
        """
        commodities_crypto = client.query(commodities_crypto_query).to_dataframe()

        # Convert month to datetime
        monthly_performance['month'] = pd.to_datetime(monthly_performance['month'])
        tech_stocks['month'] = pd.to_datetime(tech_stocks['month'])
        commodities_crypto['month'] = pd.to_datetime(commodities_crypto['month'])

        # Combine all dataframes
        all_assets = pd.merge(monthly_performance, tech_stocks, on='month')
        all_assets = pd.merge(all_assets, commodities_crypto, on='month')

        return monthly_performance, tech_stocks, commodities_crypto, all_assets

    except Exception as e:
        print(f"Error loading data from BigQuery: {e}")
        # Create sample data as fallback
        return create_sample_data()

# Create sample data if BigQuery fails
def create_sample_data():
    print("Using sample data instead of BigQuery data.")

    # Create date range
    dates = pd.date_range(start='2019-01-01', end='2023-12-31', freq='MS')
    np.random.seed(42)  # For reproducibility

    # Create monthly performance data
    monthly_performance = pd.DataFrame({
        'month': dates,
        'avg_sp500_price': np.random.normal(3000, 500, len(dates)) + np.linspace(0, 1000, len(dates)),
        'avg_nasdaq_price': np.random.normal(8000, 1000, len(dates)) + np.linspace(0, 3000, len(dates)),
        'avg_tech_price': np.random.normal(150, 30, len(dates)) + np.linspace(0, 100, len(dates)),
        'avg_commodity_price': np.random.normal(80, 15, len(dates)) + np.linspace(0, 20, len(dates)),
        'avg_crypto_price': np.random.normal(10000, 5000, len(dates)) * np.exp(np.linspace(0, 0.5, len(dates)))
    })

    # Create tech stocks data
    tech_stocks = pd.DataFrame({
        'month': dates,
        'avg_apple_price': np.random.normal(100, 20, len(dates)) + np.linspace(0, 50, len(dates)),
        'avg_microsoft_price': np.random.normal(150, 30, len(dates)) + np.linspace(0, 100, len(dates)),
        'avg_google_price': np.random.normal(1000, 200, len(dates)) + np.linspace(0, 500, len(dates)),
        'avg_amazon_price': np.random.normal(1500, 300, len(dates)) + np.linspace(0, 1000, len(dates)),
        'avg_meta_price': np.random.normal(200, 50, len(dates)) + np.linspace(0, 100, len(dates)),
        'avg_nvidia_price': np.random.normal(100, 50, len(dates)) + np.linspace(0, 300, len(dates)),
        'avg_tesla_price': np.random.normal(200, 100, len(dates)) + np.linspace(0, 500, len(dates))
    })

    # Create commodities and crypto data
    commodities_crypto = pd.DataFrame({
        'month': dates,
        'avg_gold_price': np.random.normal(1500, 100, len(dates)) + np.linspace(0, 300, len(dates)),
        'avg_crude_oil_price': np.random.normal(60, 15, len(dates)) + np.linspace(0, 20, len(dates)),
        'avg_natural_gas_price': np.random.normal(3, 1, len(dates)) + np.linspace(0, 2, len(dates)),
        'avg_bitcoin_price': np.random.normal(20000, 10000, len(dates)) * np.exp(np.linspace(0, 0.5, len(dates))),
        'avg_ethereum_price': np.random.normal(1000, 500, len(dates)) * np.exp(np.linspace(0, 0.5, len(dates)))
    })

    # Combine all dataframes
    all_assets = pd.merge(monthly_performance, tech_stocks, on='month')
    all_assets = pd.merge(all_assets, commodities_crypto, on='month')

    return monthly_performance, tech_stocks, commodities_crypto, all_assets

# Function to convert matplotlib figure to base64 image
def fig_to_base64(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=300, bbox_inches='tight')
    buf.seek(0)
    img_str = base64.b64encode(buf.read()).decode('utf-8')
    return f'<img src="data:image/png;base64,{img_str}" class="static-img">'

# Generate Market Overview visualizations
def generate_market_overview():
    monthly_performance, tech_stocks, commodities_crypto, all_assets = load_data()

    graphs_html = []

    # 1. Major Indices Price Trends
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=monthly_performance['month'],
        y=monthly_performance['avg_sp500_price'],
        mode='lines',
        name='S&P 500'
    ))
    fig.add_trace(go.Scatter(
        x=monthly_performance['month'],
        y=monthly_performance['avg_nasdaq_price'],
        mode='lines',
        name='NASDAQ'
    ))

    fig.update_layout(
        title='S&P 500 and NASDAQ Monthly Average Prices (2019-2024)',
        xaxis_title='Date',
        yaxis_title='Average Price',
        height=500,
        template='plotly_white'
    )

    graphs_html.append(f"""
    <div class="chart-container">
        <div class="chart-title">Major Indices Price Trends</div>
        {fig.to_html(full_html=False, include_plotlyjs=False)}
    </div>
    """)

    # 2. Asset Class Comparison
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=monthly_performance['month'],
        y=monthly_performance['avg_tech_price'],
        mode='lines',
        name='Tech Stocks'
    ))
    fig.add_trace(go.Scatter(
        x=monthly_performance['month'],
        y=monthly_performance['avg_commodity_price'],
        mode='lines',
        name='Commodities'
    ))
    fig.add_trace(go.Scatter(
        x=monthly_performance['month'],
        y=monthly_performance['avg_crypto_price'],
        mode='lines',
        name='Cryptocurrencies'
    ))

    fig.update_layout(
        title='Average Prices by Asset Class (2019-2024)',
        xaxis_title='Date',
        yaxis_title='Average Price',
        height=500,
        template='plotly_white'
    )

    graphs_html.append(f"""
    <div class="chart-container">
        <div class="chart-title">Asset Class Comparison</div>
        {fig.to_html(full_html=False, include_plotlyjs=False)}
    </div>
    """)

    # 3. Tech Stocks Comparison
    fig = go.Figure()
    for col in tech_stocks.columns:
        if 'avg_' in col and '_price' in col:
            fig.add_trace(go.Scatter(
                x=tech_stocks['month'],
                y=tech_stocks[col],
                mode='lines',
                name=col.replace('avg_', '').replace('_price', '').title()
            ))

    fig.update_layout(
        title='Tech Stock Prices (2019-2024)',
        xaxis_title='Date',
        yaxis_title='Price',
        height=500,
        template='plotly_white'
    )

    graphs_html.append(f"""
    <div class="chart-container">
        <div class="chart-title">Tech Stocks Comparison</div>
        {fig.to_html(full_html=False, include_plotlyjs=False)}
    </div>
    """)

    # 4. Correlation Heatmap
    correlation_columns = [
        'avg_sp500_price', 'avg_nasdaq_price', 'avg_tech_price', 'avg_commodity_price', 'avg_crypto_price',
        'avg_gold_price', 'avg_crude_oil_price', 'avg_bitcoin_price', 'avg_ethereum_price',
        'avg_apple_price', 'avg_microsoft_price', 'avg_nvidia_price'
    ]

    # Calculate correlations
    asset_corr = all_assets[correlation_columns].corr()

    # Create a heatmap with plotly
    fig = px.imshow(
        asset_corr,
        text_auto='.2f',
        color_continuous_scale='RdBu_r',
        zmin=-1,
        zmax=1,
        labels=dict(x="Asset", y="Asset", color="Correlation"),
        x=[col.replace('avg_', '').replace('_price', '').title() for col in asset_corr.columns],
        y=[col.replace('avg_', '').replace('_price', '').title() for col in asset_corr.index]
    )

    fig.update_layout(
        title='Correlation Between Different Asset Classes',
        height=700,
        template='plotly_white'
    )

    graphs_html.append(f"""
    <div class="chart-container">
        <div class="chart-title">Asset Correlation Heatmap</div>
        {fig.to_html(full_html=False, include_plotlyjs=False)}
    </div>
    """)

    # 5. Key Market Events
    # Define key market events
    events = {
        'COVID-19 Crash': '2020-03-01',
        'Recovery Start': '2020-04-01',
        'Fed Rate Hikes': '2022-01-01',
        'Banking Crisis': '2023-03-01',
        '2023 Recovery': '2023-04-01',
        'AI Boom': '2023-11-01'
    }

    # Convert event dates to datetime
    events = {k: pd.to_datetime(v) for k, v in events.items()}

    # Create a plot with event markers
    fig = go.Figure()

    # Plot S&P 500 and NASDAQ
    fig.add_trace(go.Scatter(
        x=monthly_performance['month'],
        y=monthly_performance['avg_sp500_price'],
        mode='lines',
        name='S&P 500'
    ))
    fig.add_trace(go.Scatter(
        x=monthly_performance['month'],
        y=monthly_performance['avg_nasdaq_price'],
        mode='lines',
        name='NASDAQ'
    ))

    # Add event markers as vertical lines using shapes instead of add_vline
    for event, date in events.items():
        fig.add_shape(
            type="line",
            x0=date,
            x1=date,
            y0=0,
            y1=1,
            yref="paper",
            line=dict(color="red", width=1, dash="dash")
        )

        # Add annotation for the event
        fig.add_annotation(
            x=date,
            y=1,
            yref="paper",
            text=event,
            showarrow=False,
            textangle=-90,
            xanchor="left",
            yanchor="top",
            font=dict(size=12)
        )

    fig.update_layout(
        title='Market Performance During Key Events (2019-2024)',
        xaxis_title='Date',
        yaxis_title='Average Price',
        height=500,
        template='plotly_white',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    graphs_html.append(f"""
    <div class="chart-container">
        <div class="chart-title">Market Performance During Key Events</div>
        {fig.to_html(full_html=False, include_plotlyjs=False)}
    </div>
    """)

    return "\n".join(graphs_html)

# Generate Risk and Returns Analysis visualizations
def generate_risk_returns():
    monthly_performance, tech_stocks, commodities_crypto, all_assets = load_data()

    # Set month as index for time series analysis
    monthly_data = monthly_performance.set_index('month')

    # Get asset columns
    assets = [col for col in monthly_data.columns if 'avg_' in col and '_price' in col]

    # Calculate monthly returns
    returns_data = monthly_data[assets].pct_change().dropna()

    # Rename columns for clarity
    returns_data.columns = [col.replace('avg_', '').replace('_price', '') for col in returns_data.columns]

    graphs_html = []

    # 1. Monthly Returns Heatmap
    # Extract month and year
    returns_data_reset = returns_data.reset_index()
    returns_data_reset['Year'] = returns_data_reset['month'].dt.year
    returns_data_reset['Month'] = returns_data_reset['month'].dt.month

    # Create pivot table for S&P 500
    sp500_returns = returns_data_reset.pivot_table(
        index='Year',
        columns='Month',
        values='sp500',
        aggfunc='mean'
    ) * 100  # Convert to percentage

    # Rename month columns
    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    sp500_returns.columns = month_names

    fig = px.imshow(
        sp500_returns,
        text_auto='.1f',
        color_continuous_scale='RdYlGn',
        zmin=-10,
        zmax=10,
        labels=dict(x="Month", y="Year", color="Return (%)"),
        title="S&P 500 Monthly Returns (%)"
    )

    fig.update_layout(
        height=400,
        template='plotly_white'
    )

    graphs_html.append(f"""
    <div class="chart-container">
        <div class="chart-title">S&P 500 Monthly Returns Heatmap (%)</div>
        {fig.to_html(full_html=False, include_plotlyjs=False)}
    </div>
    """)

    # 2. Calculate performance metrics
    def calculate_performance_metrics(returns, risk_free_rate=0.02, periods_per_year=12):
        """Calculate key performance metrics for each asset class"""
        # Create empty DataFrame for metrics
        metrics = pd.DataFrame(index=returns.columns)

        # Calculate annualized return (geometric mean)
        # First convert returns to gross returns (1 + r)
        gross_returns = (1 + returns)

        # Calculate the product of all gross returns
        total_gross_return = gross_returns.prod()

        # Calculate the annualized return
        n_periods = len(returns)
        metrics['Annualized Return (%)'] = (total_gross_return ** (periods_per_year / n_periods) - 1) * 100

        # Calculate annualized volatility
        metrics['Annualized Volatility (%)'] = returns.std() * np.sqrt(periods_per_year) * 100

        # Calculate Sharpe Ratio
        sharpe_ratio = (metrics['Annualized Return (%)'] / 100 - risk_free_rate) / (metrics['Annualized Volatility (%)'] / 100)
        metrics['Sharpe Ratio'] = sharpe_ratio

        # Calculate maximum drawdown
        cumulative_returns = (1 + returns).cumprod()
        running_max = cumulative_returns.cummax()
        drawdown = (cumulative_returns / running_max - 1) * 100
        metrics['Maximum Drawdown (%)'] = drawdown.min()

        return metrics

    # Calculate performance metrics
    performance_metrics = calculate_performance_metrics(returns_data)

    # Create a risk-return scatter plot
    fig = px.scatter(
        x=performance_metrics['Annualized Volatility (%)'],
        y=performance_metrics['Annualized Return (%)'],
        text=performance_metrics.index,
        size=abs(performance_metrics['Sharpe Ratio']) * 5,  # Size based on absolute Sharpe ratio
        color=performance_metrics['Sharpe Ratio'],  # Color based on Sharpe ratio
        color_continuous_scale='RdYlGn',  # Red for low Sharpe, Green for high Sharpe
        labels={
            'x': 'Annualized Volatility (%)',
            'y': 'Annualized Return (%)',
            'color': 'Sharpe Ratio',
            'size': 'Sharpe Ratio'
        },
        title='Risk vs. Return Analysis'
    )

    fig.update_traces(
        textposition='top center',
        marker=dict(sizemin=5)
    )

    fig.update_layout(
        height=500,
        template='plotly_white',
        xaxis=dict(zeroline=True, zerolinewidth=1, zerolinecolor='red', gridcolor='lightgray'),
        yaxis=dict(zeroline=True, zerolinewidth=1, zerolinecolor='red', gridcolor='lightgray')
    )

    graphs_html.append(f"""
    <div class="chart-container">
        <div class="chart-title">Risk vs. Return Analysis</div>
        {fig.to_html(full_html=False, include_plotlyjs=False)}
    </div>
    """)

    # 3. Rolling metrics
    window = 12  # 12-month rolling window

    # Calculate rolling returns
    rolling_returns = returns_data.rolling(window=window).mean() * 12 * 100  # Annualized

    # Calculate rolling volatility
    rolling_volatility = returns_data.rolling(window=window).std() * np.sqrt(12) * 100  # Annualized

    # Calculate rolling Sharpe ratio (assuming risk-free rate of 2%)
    risk_free_monthly = 0.02 / 12  # Monthly risk-free rate
    rolling_sharpe = (returns_data.rolling(window=window).mean() - risk_free_monthly) / returns_data.rolling(window=window).std() * np.sqrt(12)

    # Plot rolling returns
    fig = go.Figure()

    for asset in rolling_returns.columns:
        fig.add_trace(go.Scatter(
            x=rolling_returns.index,
            y=rolling_returns[asset],
            mode='lines',
            name=asset
        ))

    fig.update_layout(
        title=f'{window}-Month Rolling Annualized Returns',
        xaxis_title='Date',
        yaxis_title='Return (%)',
        height=500,
        template='plotly_white',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    graphs_html.append(f"""
    <div class="chart-container">
        <div class="chart-title">Rolling Annualized Returns</div>
        {fig.to_html(full_html=False, include_plotlyjs=False)}
    </div>
    """)

    # Plot rolling volatility
    fig = go.Figure()

    for asset in rolling_volatility.columns:
        fig.add_trace(go.Scatter(
            x=rolling_volatility.index,
            y=rolling_volatility[asset],
            mode='lines',
            name=asset
        ))

    fig.update_layout(
        title=f'{window}-Month Rolling Annualized Volatility',
        xaxis_title='Date',
        yaxis_title='Volatility (%)',
        height=500,
        template='plotly_white',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    graphs_html.append(f"""
    <div class="chart-container">
        <div class="chart-title">Rolling Annualized Volatility</div>
        {fig.to_html(full_html=False, include_plotlyjs=False)}
    </div>
    """)

    # 4. Cumulative Returns
    cumulative_returns = (1 + returns_data).cumprod()

    fig = go.Figure()

    for asset in cumulative_returns.columns:
        fig.add_trace(go.Scatter(
            x=cumulative_returns.index,
            y=cumulative_returns[asset],
            mode='lines',
            name=asset
        ))

    fig.update_layout(
        title='Cumulative Returns (Growth of $1)',
        xaxis_title='Date',
        yaxis_title='Value',
        height=500,
        template='plotly_white',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    graphs_html.append(f"""
    <div class="chart-container">
        <div class="chart-title">Cumulative Returns</div>
        {fig.to_html(full_html=False, include_plotlyjs=False)}
    </div>
    """)

    return "\n".join(graphs_html)

# Generate Market Trends Analysis visualizations
def generate_market_trends():
    monthly_performance, tech_stocks, commodities_crypto, all_assets = load_data()

    # Set month as index for time series analysis
    trend_data = monthly_performance.copy().set_index('month')

    graphs_html = []

    # 1. Calculate moving averages for each asset class
    def calculate_moving_averages(data, windows=[3, 6, 12]):
        """Calculate moving averages for the given windows (in months)"""
        result = data.copy()

        for window in windows:
            for col in data.columns:
                if 'avg_' in col and '_price' in col:
                    result[f'{col}_MA{window}'] = data[col].rolling(window=window).mean()

        return result

    # Calculate moving averages
    ma_data = calculate_moving_averages(trend_data)

    # Plot moving averages for S&P 500
    asset_col = 'avg_sp500_price'
    windows = [3, 6, 12]

    fig = go.Figure()

    # Plot price
    fig.add_trace(go.Scatter(
        x=ma_data.index,
        y=ma_data[asset_col],
        mode='lines',
        name='S&P 500',
        line=dict(width=2)
    ))

    # Plot moving averages
    colors = ['red', 'green', 'blue']
    for i, window in enumerate(windows):
        ma_col = f'{asset_col}_MA{window}'
        if ma_col in ma_data.columns:
            fig.add_trace(go.Scatter(
                x=ma_data.index,
                y=ma_data[ma_col],
                mode='lines',
                name=f'{window}-Month MA',
                line=dict(width=1.5, color=colors[i % len(colors)])
            ))

    fig.update_layout(
        title='Moving Averages for S&P 500',
        xaxis_title='Date',
        yaxis_title='Price',
        height=500,
        template='plotly_white',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    graphs_html.append(f"""
    <div class="chart-container">
        <div class="chart-title">S&P 500 Moving Averages</div>
        {fig.to_html(full_html=False, include_plotlyjs=False)}
    </div>
    """)

    # 2. Identify trends based on moving average crossovers
    def identify_trends(data, short_window=3, long_window=12):
        """Identify trends based on moving average crossovers"""
        trends = pd.DataFrame(index=data.index)

        for col in data.columns:
            if 'avg_' in col and '_price' in col:
                short_ma = f'{col}_MA{short_window}'
                long_ma = f'{col}_MA{long_window}'

                if short_ma in data.columns and long_ma in data.columns:
                    # 1 for bullish (short MA > long MA), -1 for bearish, 0 for neutral/undefined
                    asset_name = col.replace('avg_', '').replace('_price', '')
                    trends[f'{asset_name}_trend'] = np.where(
                        data[short_ma] > data[long_ma], 1,
                        np.where(data[short_ma] < data[long_ma], -1, 0)
                    )

        # Drop rows with NaN values (due to the rolling window)
        trends = trends.dropna()

        return trends

    # Identify trends
    trends = identify_trends(ma_data)

    # Plot the trends over time
    fig = go.Figure()

    # Plot each asset's trend
    for col in trends.columns:
        fig.add_trace(go.Scatter(
            x=trends.index,
            y=trends[col],
            mode='lines',
            name=col
        ))

    # Add reference lines
    fig.add_shape(
        type="line",
        x0=trends.index.min(),
        x1=trends.index.max(),
        y0=0,
        y1=0,
        line=dict(color="black", width=1, dash="dash")
    )

    # Add colored regions for bullish/bearish
    fig.add_shape(
        type="rect",
        x0=trends.index.min(),
        x1=trends.index.max(),
        y0=1,
        y1=1.5,
        fillcolor="green",
        opacity=0.1,
        layer="below",
        line_width=0
    )

    fig.add_shape(
        type="rect",
        x0=trends.index.min(),
        x1=trends.index.max(),
        y0=-1,
        y1=-1.5,
        fillcolor="red",
        opacity=0.1,
        layer="below",
        line_width=0
    )

    fig.update_layout(
        title='Market Trends Based on Moving Average Crossovers',
        xaxis_title='Date',
        yaxis_title='Trend Indicator',
        height=500,
        template='plotly_white',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        yaxis=dict(range=[-1.5, 1.5])
    )

    graphs_html.append(f"""
    <div class="chart-container">
        <div class="chart-title">Market Trends Indicator</div>
        {fig.to_html(full_html=False, include_plotlyjs=False)}
    </div>
    """)

    # 3. Calculate momentum indicators
    def calculate_momentum(data, periods=[1, 3, 6, 12]):
        """Calculate momentum over different periods"""
        momentum = pd.DataFrame(index=data.index)

        for col in data.columns:
            if 'avg_' in col and '_price' in col:
                for period in periods:
                    # Momentum is the percentage change over the period
                    asset_name = col.replace('avg_', '').replace('_price', '')
                    momentum[f'{asset_name}_momentum_{period}m'] = data[col].pct_change(periods=period) * 100

        return momentum

    # Calculate momentum
    momentum = calculate_momentum(trend_data)

    # Create momentum heatmap for the last 12 months
    recent_momentum = momentum.tail(12)

    # Reshape for heatmap
    assets = [col.split('_momentum_')[0] for col in momentum.columns if '_momentum_1m' in col]
    periods = [1, 3, 6, 12]

    heatmap_data = []
    for asset in assets:
        row = []
        for period in periods:
            # Get the most recent momentum value for this asset and period
            value = recent_momentum[f'{asset}_momentum_{period}m'].iloc[-1]
            row.append(value)
        heatmap_data.append(row)

    # Create DataFrame for heatmap
    heatmap_df = pd.DataFrame(heatmap_data, index=assets, columns=[f'{p}m' for p in periods])

    # Plot heatmap
    fig = px.imshow(
        heatmap_df,
        text_auto='.1f',
        color_continuous_scale='RdYlGn',
        labels=dict(x="Time Period", y="Asset", color="Momentum (%)"),
        x=[f'{p}m' for p in periods],
        y=assets
    )

    fig.update_layout(
        title='Asset Momentum Heatmap (Most Recent)',
        height=500,
        template='plotly_white'
    )

    graphs_html.append(f"""
    <div class="chart-container">
        <div class="chart-title">Asset Momentum Heatmap</div>
        {fig.to_html(full_html=False, include_plotlyjs=False)}
    </div>
    """)

    # 4. Analyze seasonality
    def analyze_seasonality(data, asset_col):
        """Analyze monthly seasonality for an asset"""
        # Extract month from the index
        seasonality_data = data[[asset_col]].copy()
        seasonality_data['month_num'] = seasonality_data.index.month
        seasonality_data['year'] = seasonality_data.index.year

        # Calculate monthly returns
        seasonality_data['monthly_return'] = seasonality_data[asset_col].pct_change() * 100

        # Group by month and calculate average return
        monthly_avg = seasonality_data.groupby('month_num')['monthly_return'].mean()

        # Create a DataFrame with month names
        month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        seasonality_df = pd.DataFrame({
            'Month': month_names,
            'Average Return (%)': monthly_avg.values
        })

        return seasonality_df

    # Analyze seasonality for all assets
    assets_cols = [col for col in trend_data.columns if 'avg_' in col and '_price' in col]
    seasonality_results = {}

    for asset_col in assets_cols:
        asset_name = asset_col.replace('avg_', '').replace('_price', '')
        seasonality_results[asset_name] = analyze_seasonality(trend_data, asset_col)

    # Create a heatmap of monthly seasonality for all assets
    seasonality_heatmap = pd.DataFrame(index=range(1, 13))

    for asset, data in seasonality_results.items():
        seasonality_heatmap[asset] = data['Average Return (%)'].values

    # Set month names as index
    seasonality_heatmap.index = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

    # Plot heatmap
    fig = px.imshow(
        seasonality_heatmap,
        text_auto='.1f',
        color_continuous_scale='RdYlGn',
        zmin=-5,
        zmax=5,
        labels=dict(x="Asset", y="Month", color="Average Return (%)")
    )

    fig.update_layout(
        title='Monthly Seasonality Heatmap Across Assets',
        height=600,
        template='plotly_white'
    )

    graphs_html.append(f"""
    <div class="chart-container">
        <div class="chart-title">Monthly Seasonality Heatmap</div>
        {fig.to_html(full_html=False, include_plotlyjs=False)}
    </div>
    """)

    return "\n".join(graphs_html)

# Generate Portfolio Optimization visualizations
def generate_portfolio_optimization():
    monthly_performance, tech_stocks, commodities_crypto, all_assets = load_data()

    # Set month as index for time series analysis
    portfolio_data = monthly_performance.copy().set_index('month')

    # Select only the price columns for our analysis
    asset_columns = [col for col in portfolio_data.columns if 'avg_' in col and '_price' in col]
    price_data = portfolio_data[asset_columns]

    # Calculate monthly returns
    returns_data = price_data.pct_change().dropna()

    # Create cleaner column names for display
    display_columns = [col.replace('avg_', '').replace('_price', '') for col in returns_data.columns]
    returns_data.columns = display_columns

    # Calculate mean returns and covariance matrix
    mean_returns = returns_data.mean()
    cov_matrix = returns_data.cov()

    graphs_html = []

    # 1. Display annualized statistics
    annualized_returns = mean_returns * 12 * 100  # Convert to percentage
    annualized_volatility = returns_data.std() * np.sqrt(12) * 100  # Convert to percentage
    sharpe_ratio = annualized_returns / annualized_volatility

    # Create a DataFrame for display
    stats_df = pd.DataFrame({
        'Annualized Return (%)': annualized_returns,
        'Annualized Volatility (%)': annualized_volatility,
        'Sharpe Ratio': sharpe_ratio
    })

    # Create a table visualization
    fig = go.Figure(data=[go.Table(
        header=dict(
            values=['Asset', 'Annualized Return (%)', 'Annualized Volatility (%)', 'Sharpe Ratio'],
            fill_color='#343a40',
            align='left',
            font=dict(color='white', size=12)
        ),
        cells=dict(
            values=[
                stats_df.index,
                stats_df['Annualized Return (%)'].round(2),
                stats_df['Annualized Volatility (%)'].round(2),
                stats_df['Sharpe Ratio'].round(2)
            ],
            fill_color='white',
            align='left'
        )
    )])

    fig.update_layout(
        title='Asset Performance Metrics',
        height=400,
        margin=dict(l=0, r=0, t=40, b=0)
    )

    graphs_html.append(f"""
    <div class="chart-container">
        <div class="chart-title">Asset Performance Metrics</div>
        {fig.to_html(full_html=False, include_plotlyjs=False)}
    </div>
    """)

    # 2. Portfolio optimization functions
    def portfolio_annualized_performance(weights, mean_returns, cov_matrix, risk_free_rate=0.02, periods_per_year=12):
        """Calculate annualized return and volatility for a portfolio"""
        weights = np.array(weights)
        mean_returns = np.array(mean_returns)

        portfolio_return = np.sum(mean_returns * weights) * periods_per_year
        portfolio_volatility = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights))) * np.sqrt(periods_per_year)
        sharpe_ratio = (portfolio_return - risk_free_rate) / portfolio_volatility

        return portfolio_return, portfolio_volatility, sharpe_ratio

    def negative_sharpe_ratio(weights, mean_returns, cov_matrix, risk_free_rate=0.02, periods_per_year=12):
        """Return negative Sharpe ratio (for minimization)"""
        return -portfolio_annualized_performance(weights, mean_returns, cov_matrix, risk_free_rate, periods_per_year)[2]

    def max_sharpe_ratio(mean_returns, cov_matrix, risk_free_rate=0.02, periods_per_year=12, constraint_set=(0, 1)):
        """Find the portfolio weights that maximize the Sharpe ratio"""
        num_assets = len(mean_returns)
        args = (mean_returns, cov_matrix, risk_free_rate, periods_per_year)

        constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
        bounds = tuple(constraint_set for asset in range(num_assets))

        initial_guess = num_assets * [1. / num_assets]

        result = sco.minimize(
            negative_sharpe_ratio,
            initial_guess,
            args=args,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints
        )

        return result

    def portfolio_volatility(weights, mean_returns, cov_matrix, periods_per_year=12):
        """Calculate portfolio volatility"""
        weights = np.array(weights)
        return np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights))) * np.sqrt(periods_per_year)

    def min_variance(mean_returns, cov_matrix, periods_per_year=12, constraint_set=(0, 1)):
        """Find the portfolio weights that minimize variance"""
        num_assets = len(mean_returns)
        args = (mean_returns, cov_matrix, periods_per_year)

        constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
        bounds = tuple(constraint_set for asset in range(num_assets))

        initial_guess = num_assets * [1. / num_assets]

        result = sco.minimize(
            portfolio_volatility,
            initial_guess,
            args=args,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints
        )

        return result

    def efficient_frontier(mean_returns, cov_matrix, returns_range, periods_per_year=12, constraint_set=(0, 1)):
        """Calculate the efficient frontier for a range of target returns"""
        num_assets = len(mean_returns)
        results = []

        for target in returns_range:
            constraints = (
                {'type': 'eq', 'fun': lambda x: np.sum(x) - 1},
                {'type': 'eq', 'fun': lambda x: portfolio_annualized_performance(x, mean_returns, cov_matrix, 0, periods_per_year)[0] - target}
            )

            bounds = tuple(constraint_set for asset in range(num_assets))

            initial_guess = num_assets * [1. / num_assets]

            result = sco.minimize(
                portfolio_volatility,
                initial_guess,
                args=(mean_returns, cov_matrix, periods_per_year),
                method='SLSQP',
                bounds=bounds,
                constraints=constraints
            )

            if result['success']:
                results.append(result['fun'])
            else:
                results.append(np.nan)

        return results

    # 3. Calculate optimal portfolios
    # Maximum Sharpe ratio portfolio
    max_sharpe_result = max_sharpe_ratio(mean_returns, cov_matrix)
    max_sharpe_weights = max_sharpe_result['x']
    max_sharpe_performance = portfolio_annualized_performance(max_sharpe_weights, mean_returns, cov_matrix)

    # Minimum variance portfolio
    min_var_result = min_variance(mean_returns, cov_matrix)
    min_var_weights = min_var_result['x']
    min_var_performance = portfolio_annualized_performance(min_var_weights, mean_returns, cov_matrix)

    # Equal weight portfolio (for comparison)
    equal_weights = np.array([1/len(mean_returns)] * len(mean_returns))
    equal_performance = portfolio_annualized_performance(equal_weights, mean_returns, cov_matrix)

    # 4. Create pie charts for optimal portfolios
    # Maximum Sharpe Ratio Portfolio
    max_sharpe_df = pd.DataFrame({
        'Asset': display_columns,
        'Weight': max_sharpe_weights
    })

    fig = px.pie(
        max_sharpe_df,
        values='Weight',
        names='Asset',
        title='Maximum Sharpe Ratio Portfolio Allocation',
        hover_data=['Weight'],
        labels={'Weight': 'Allocation'},
        color_discrete_sequence=px.colors.qualitative.Pastel
    )

    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        marker=dict(line=dict(color='#000000', width=1))
    )

    fig.update_layout(
        height=500
    )

    graphs_html.append(f"""
    <div class="chart-container">
        <div class="chart-title">Maximum Sharpe Ratio Portfolio Allocation</div>
        {fig.to_html(full_html=False, include_plotlyjs=False)}
    </div>
    """)

    # Minimum Variance Portfolio
    min_var_df = pd.DataFrame({
        'Asset': display_columns,
        'Weight': min_var_weights
    })

    fig = px.pie(
        min_var_df,
        values='Weight',
        names='Asset',
        title='Minimum Variance Portfolio Allocation',
        hover_data=['Weight'],
        labels={'Weight': 'Allocation'},
        color_discrete_sequence=px.colors.qualitative.Pastel
    )

    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        marker=dict(line=dict(color='#000000', width=1))
    )

    fig.update_layout(
        height=500
    )

    graphs_html.append(f"""
    <div class="chart-container">
        <div class="chart-title">Minimum Variance Portfolio Allocation</div>
        {fig.to_html(full_html=False, include_plotlyjs=False)}
    </div>
    """)

    # 5. Calculate efficient frontier
    target_returns = np.linspace(min_var_performance[0], max_sharpe_performance[0] * 1.2, 50)
    efficient_risk = efficient_frontier(mean_returns, cov_matrix, target_returns)

    # Create a DataFrame for the efficient frontier
    efficient_frontier_df = pd.DataFrame({
        'Returns': target_returns,
        'Volatility': efficient_risk
    })

    # Remove any NaN values (optimization failures)
    efficient_frontier_df = efficient_frontier_df.dropna()

    # Plot efficient frontier
    fig = go.Figure()

    # Add efficient frontier
    fig.add_trace(go.Scatter(
        x=efficient_frontier_df['Volatility'],
        y=efficient_frontier_df['Returns'],
        mode='lines',
        name='Efficient Frontier',
        line=dict(color='blue', width=3)
    ))

    # Add individual assets
    for i, asset in enumerate(display_columns):
        fig.add_trace(go.Scatter(
            x=[annualized_volatility[i] / 100],  # Convert from percentage
            y=[annualized_returns[i] / 100],     # Convert from percentage
            mode='markers',
            marker=dict(size=12),
            name=asset
        ))

    # Add optimal portfolios
    fig.add_trace(go.Scatter(
        x=[max_sharpe_performance[1]],
        y=[max_sharpe_performance[0]],
        mode='markers',
        marker=dict(
            color='red',
            size=20,
            symbol='star'
        ),
        name='Maximum Sharpe Ratio'
    ))

    fig.add_trace(go.Scatter(
        x=[min_var_performance[1]],
        y=[min_var_performance[0]],
        mode='markers',
        marker=dict(
            color='green',
            size=18,
            symbol='diamond'
        ),
        name='Minimum Variance'
    ))

    fig.add_trace(go.Scatter(
        x=[equal_performance[1]],
        y=[equal_performance[0]],
        mode='markers',
        marker=dict(
            color='yellow',
            size=16,
            symbol='square'
        ),
        name='Equal Weight'
    ))

    fig.update_layout(
        title='Efficient Frontier with Optimal Portfolios',
        xaxis_title='Expected Annual Volatility',
        yaxis_title='Expected Annual Return',
        height=600,
        template='plotly_white',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    graphs_html.append(f"""
    <div class="chart-container">
        <div class="chart-title">Efficient Frontier with Optimal Portfolios</div>
        {fig.to_html(full_html=False, include_plotlyjs=False)}
    </div>
    """)

    # 6. Portfolio performance metrics
    metrics_html = f"""
    <div class="row">
        <div class="col-md-4">
            <div class="metrics-card">
                <div class="metrics-value">{max_sharpe_performance[0]:.2%}</div>
                <div class="metrics-label">Max Sharpe Return</div>
            </div>
        </div>
        <div class="col-md-4">
            <div class="metrics-card">
                <div class="metrics-value">{max_sharpe_performance[1]:.2%}</div>
                <div class="metrics-label">Max Sharpe Volatility</div>
            </div>
        </div>
        <div class="col-md-4">
            <div class="metrics-card">
                <div class="metrics-value">{max_sharpe_performance[2]:.2f}</div>
                <div class="metrics-label">Max Sharpe Ratio</div>
            </div>
        </div>
    </div>
    <div class="row mt-3">
        <div class="col-md-4">
            <div class="metrics-card">
                <div class="metrics-value">{min_var_performance[0]:.2%}</div>
                <div class="metrics-label">Min Variance Return</div>
            </div>
        </div>
        <div class="col-md-4">
            <div class="metrics-card">
                <div class="metrics-value">{min_var_performance[1]:.2%}</div>
                <div class="metrics-label">Min Variance Volatility</div>
            </div>
        </div>
        <div class="col-md-4">
            <div class="metrics-card">
                <div class="metrics-value">{min_var_performance[2]:.2f}</div>
                <div class="metrics-label">Min Variance Sharpe</div>
            </div>
        </div>
    </div>
    """

    graphs_html.append(f"""
    <div class="chart-container">
        <div class="chart-title">Portfolio Performance Metrics</div>
        {metrics_html}
    </div>
    """)

    return "\n".join(graphs_html)

# Main function to generate the HTML dashboard
def generate_dashboard():
    # Generate all visualizations
    market_overview_graphs = generate_market_overview()
    risk_returns_graphs = generate_risk_returns()
    market_trends_graphs = generate_market_trends()
    portfolio_optimization_graphs = generate_portfolio_optimization()

    # Format the HTML content
    formatted_html = html_content.format(
        market_overview_graphs=market_overview_graphs,
        risk_returns_graphs=risk_returns_graphs,
        market_trends_graphs=market_trends_graphs,
        portfolio_optimization_graphs=portfolio_optimization_graphs
    )

    # Write to file
    with open('stock_market_dashboard.html', 'w') as f:
        f.write(formatted_html)

    print("HTML dashboard created: stock_market_dashboard.html")

# Run the dashboard generator
if __name__ == "__main__":
    generate_dashboard()