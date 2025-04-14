import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from google.cloud import bigquery
import scipy.optimize as sco

# Set page configuration
st.set_page_config(
    page_title="Stock Market Analysis Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add custom CSS
st.markdown("""
<style>
    .main {
        padding: 1rem 1rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #f0f2f6;
        border-radius: 4px 4px 0 0;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #e6f0ff;
    }
    h1, h2, h3 {
        color: #1E3A8A;
    }
    .plot-container {
        border-radius: 5px;
        background-color: white;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        padding: 10px;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# Title and introduction
st.title("📊 Stock Market Analysis Dashboard")
st.markdown("""
This dashboard provides comprehensive analysis of stock market data from 2019-2024, 
including performance metrics, correlation analysis, portfolio optimization, and market trends.
""")

# Sidebar for controls
st.sidebar.header("Dashboard Controls")

# Function to load data from BigQuery
@st.cache_data(ttl=3600)  # Cache data for 1 hour
def load_data_from_bigquery():
    try:
        # Initialize BigQuery client
        client = bigquery.Client()
        
        # Query monthly performance data
        query = """
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
        
        monthly_performance = client.query(query).to_dataframe()
        
        # Convert month to datetime
        monthly_performance['month'] = pd.to_datetime(monthly_performance['month'])
        
        return monthly_performance
    
    except Exception as e:
        st.error(f"Error loading data from BigQuery: {e}")
        # Return sample data as fallback
        return create_sample_data()

# Function to create sample data if BigQuery fails
def create_sample_data():
    st.warning("Using sample data instead of BigQuery data.")
    
    # Create date range
    dates = pd.date_range(start='2019-01-01', end='2023-12-31', freq='MS')
    
    # Create sample data
    np.random.seed(42)  # For reproducibility
    
    # Starting values
    sp500_start = 2500
    nasdaq_start = 7000
    tech_start = 100
    commodity_start = 500
    crypto_start = 2000
    
    # Create random walk with drift
    def random_walk(start, steps, drift=0.005, volatility=0.03):
        returns = np.random.normal(drift, volatility, steps)
        prices = [start]
        for ret in returns:
            prices.append(prices[-1] * (1 + ret))
        return prices[1:]  # Skip the start value
    
    # Generate sample data
    sample_data = pd.DataFrame({
        'month': dates,
        'avg_sp500_price': random_walk(sp500_start, len(dates)),
        'avg_nasdaq_price': random_walk(nasdaq_start, len(dates), drift=0.007),
        'avg_tech_price': random_walk(tech_start, len(dates), drift=0.008),
        'avg_commodity_price': random_walk(commodity_start, len(dates), drift=0.003),
        'avg_crypto_price': random_walk(crypto_start, len(dates), drift=0.01, volatility=0.1)
    })
    
    return sample_data

# Load data
with st.spinner("Loading data from BigQuery..."):
    monthly_performance = load_data_from_bigquery()

# Set month as index for some calculations
monthly_data = monthly_performance.copy().set_index('month')

# Create tabs for different analyses
tab1, tab2, tab3, tab4 = st.tabs([
    "📈 Performance Analysis", 
    "🔄 Correlation Analysis", 
    "💼 Portfolio Optimization",
    "📊 Market Trends"
])

# Tab 1: Performance Analysis
with tab1:
    st.header("Stock Market Performance")
    
    # Date range selector
    date_range = st.sidebar.date_input(
        "Select Date Range",
        value=[monthly_performance['month'].min().date(), monthly_performance['month'].max().date()],
        min_value=monthly_performance['month'].min().date(),
        max_value=monthly_performance['month'].max().date()
    )
    
    # Filter data by date range
    if len(date_range) == 2:
        start_date, end_date = date_range
        filtered_data = monthly_performance[
            (monthly_performance['month'].dt.date >= start_date) & 
            (monthly_performance['month'].dt.date <= end_date)
        ]
    else:
        filtered_data = monthly_performance
    
    # Asset selector
    assets = [col for col in monthly_performance.columns if 'avg_' in col and '_price' in col]
    selected_assets = st.sidebar.multiselect(
        "Select Assets to Display",
        assets,
        default=assets,
        format_func=lambda x: x.replace('avg_', '').replace('_price', '').upper()
    )
    
    if not selected_assets:
        st.warning("Please select at least one asset to display.")
    else:
        # Price trends
        st.subheader("Price Trends")
        
        fig = go.Figure()
        
        for asset in selected_assets:
            fig.add_trace(go.Scatter(
                x=filtered_data['month'],
                y=filtered_data[asset],
                mode='lines',
                name=asset.replace('avg_', '').replace('_price', '').upper()
            ))
        
        fig.update_layout(
            height=500,
            xaxis_title="Date",
            yaxis_title="Price",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(l=40, r=40, t=40, b=40),
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Calculate returns
        returns_data = monthly_data[assets].pct_change().dropna()
        returns_data.columns = [col.replace('avg_', '').replace('_price', '') for col in returns_data.columns]
        
        # Performance metrics
        st.subheader("Performance Metrics")
        
        # Calculate annualized statistics
        annualized_returns = returns_data.mean() * 12 * 100  # Convert to percentage
        annualized_volatility = returns_data.std() * np.sqrt(12) * 100  # Convert to percentage
        sharpe_ratio = annualized_returns / annualized_volatility
        
        # Create metrics DataFrame
        metrics_df = pd.DataFrame({
            'Annualized Return (%)': annualized_returns,
            'Annualized Volatility (%)': annualized_volatility,
            'Sharpe Ratio': sharpe_ratio
        })
        
        # Display metrics
        st.dataframe(metrics_df.style.format('{:.2f}'))
        
        # Risk-Return scatter plot
        st.subheader("Risk vs. Return Analysis")
        
        fig = px.scatter(
            x=annualized_volatility,
            y=annualized_returns,
            text=returns_data.columns,
            size=abs(sharpe_ratio) * 5,
            color=sharpe_ratio,
            color_continuous_scale='RdYlGn',
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
            xaxis=dict(zeroline=True, zerolinewidth=1, zerolinecolor='red', gridcolor='lightgray'),
            yaxis=dict(zeroline=True, zerolinewidth=1, zerolinecolor='red', gridcolor='lightgray'),
        )
        
        st.plotly_chart(fig, use_container_width=True)

# Tab 2: Correlation Analysis
with tab2:
    st.header("Correlation Analysis")
    
    # Calculate correlation matrix
    returns_data = monthly_data[assets].pct_change().dropna()
    returns_data.columns = [col.replace('avg_', '').replace('_price', '') for col in returns_data.columns]
    correlation_matrix = returns_data.corr()
    
    # Correlation heatmap
    st.subheader("Correlation Heatmap")
    
    fig = px.imshow(
        correlation_matrix,
        text_auto='.2f',
        color_continuous_scale='RdBu_r',
        zmin=-1,
        zmax=1,
        aspect="auto"
    )
    
    fig.update_layout(
        height=600,
        xaxis=dict(tickangle=-45),
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Rolling correlation
    st.subheader("Rolling Correlation")
    
    # Asset selector for rolling correlation
    corr_assets = st.multiselect(
        "Select two assets to analyze rolling correlation",
        returns_data.columns,
        default=list(returns_data.columns)[:2] if len(returns_data.columns) >= 2 else [],
        max_selections=2
    )
    
    if len(corr_assets) == 2:
        # Window selector
        window = st.slider("Rolling Window (months)", min_value=3, max_value=24, value=12, step=1)
        
        # Calculate rolling correlation
        rolling_corr = returns_data[corr_assets].rolling(window=window).corr()
        rolling_corr = rolling_corr.reset_index()
        rolling_corr = rolling_corr[rolling_corr['level_1'] == corr_assets[0]]
        rolling_corr = rolling_corr.set_index('month')[[corr_assets[1]]]
        
        # Plot rolling correlation
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=rolling_corr.index,
            y=rolling_corr[corr_assets[1]],
            mode='lines',
            name=f'{corr_assets[0]} vs {corr_assets[1]}'
        ))
        
        fig.add_shape(
            type="line",
            x0=rolling_corr.index.min(),
            x1=rolling_corr.index.max(),
            y0=0,
            y1=0,
            line=dict(color="red", width=1, dash="dash")
        )
        
        fig.update_layout(
            height=400,
            xaxis_title="Date",
            yaxis_title="Correlation",
            yaxis=dict(range=[-1, 1]),
            title=f"{window}-Month Rolling Correlation"
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Please select exactly two assets to analyze their rolling correlation.")

# Tab 3: Portfolio Optimization
with tab3:
    st.header("Portfolio Optimization")
    
    # Calculate returns
    returns_data = monthly_data[assets].pct_change().dropna()
    returns_data.columns = [col.replace('avg_', '').replace('_price', '') for col in returns_data.columns]
    
    # Calculate mean returns and covariance matrix
    mean_returns = returns_data.mean()
    cov_matrix = returns_data.cov()
    
    # Portfolio optimization functions
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
    
    # Risk-free rate selector
    risk_free_rate = st.sidebar.slider("Risk-Free Rate (%)", min_value=0.0, max_value=5.0, value=2.0, step=0.1) / 100
    
    # Calculate optimal portfolios
    with st.spinner("Calculating optimal portfolios..."):
        # Maximum Sharpe ratio portfolio
        max_sharpe_result = max_sharpe_ratio(mean_returns, cov_matrix, risk_free_rate)
        max_sharpe_weights = max_sharpe_result['x']
        max_sharpe_performance = portfolio_annualized_performance(max_sharpe_weights, mean_returns, cov_matrix, risk_free_rate)
        
        # Minimum variance portfolio
        min_var_result = min_variance(mean_returns, cov_matrix)
        min_var_weights = min_var_result['x']
        min_var_performance = portfolio_annualized_performance(min_var_weights, mean_returns, cov_matrix, risk_free_rate)
        
        # Equal weight portfolio
        equal_weights = np.array([1/len(mean_returns)] * len(mean_returns))
        equal_performance = portfolio_annualized_performance(equal_weights, mean_returns, cov_matrix, risk_free_rate)
    
    # Display optimal portfolios
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("Maximum Sharpe Ratio")
        st.metric("Expected Return", f"{max_sharpe_performance[0]:.2%}")
        st.metric("Expected Volatility", f"{max_sharpe_performance[1]:.2%}")
        st.metric("Sharpe Ratio", f"{max_sharpe_performance[2]:.2f}")
    
    with col2:
        st.subheader("Minimum Variance")
        st.metric("Expected Return", f"{min_var_performance[0]:.2%}")
        st.metric("Expected Volatility", f"{min_var_performance[1]:.2%}")
        st.metric("Sharpe Ratio", f"{min_var_performance[2]:.2f}")
    
    with col3:
        st.subheader("Equal Weight")
        st.metric