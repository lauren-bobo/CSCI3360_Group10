import sys
from pathlib import Path
from src.data.API.pipeline import setup_kaggle_auth, download_and_save_dataset, load_config, load_data, prepare_data
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
import os
   
output_dir = Path("bin/data/figs")
output_dir.mkdir(parents=True, exist_ok=True)

"""When run by main in this class, this will make a chart of every stock's historical performance"""
def plot_historical_performance_per_stock(grouped_data):
    """Plot historical performance of each stock's open and close prices in subplots."""
    print("Plotting historical performance of each stock...")
    # Set the number of subplots
    num_stocks = len(grouped_data['Ticker'].unique())
    fig, axes = plt.subplots(nrows=num_stocks, ncols=1, figsize=(12, 6 * num_stocks), sharex=True)

    for ax, ticker in zip(axes, grouped_data['Ticker'].unique()):
        stock_data = grouped_data[grouped_data['Ticker'] == ticker]
        
        ax.plot(stock_data['Date'], stock_data['Open'], label='Open Price', color='blue')
        ax.plot(stock_data['Date'], stock_data['Close'], label='Close Price', color='orange')
        
        ax.set_title(f'Historical Performance of {ticker}')
        ax.set_ylabel('Price')
        ax.legend()
        ax.tick_params(axis='x', rotation=45)

    plt.xlabel('Date')
    plt.tight_layout()
    
    # Save the figure
    plt.savefig(output_dir / 'historical_stock_performance.png')
    plt.close()
"""when run, this will show volatility of each stock in a bar chart"""
def chart_volatility_per_stock(data):
    """Plot the volatility of each stock in subplots."""
    print("Plotting stock volatility...")
    # Calculate daily returns
    data['Return'] = data.groupby('Ticker')['Close'].pct_change()
    
    # Calculate volatility (standard deviation of returns)
    volatility = data.groupby('Ticker')['Return'].std()

    # Set up the figure and axes
    fig, ax = plt.subplots(figsize=(12, 8))

    # Plot volatility for each stock
    sns.barplot(x=volatility.index, y=volatility.values, ax=ax)

    # Set plot title and labels
    ax.set_title('Volatility of Each Stock', fontsize=16)
    ax.legend(loc='upper left', fontsize=10, frameon=True)
    ax.set_xlabel('Stock', fontsize=14)
    ax.set_ylabel('Volatility', fontsize=14)
    ax.tick_params(axis='x', labelsize=12)
    ax.tick_params(axis='y', labelsize=12)

    # Save the figure
    plt.savefig(output_dir / 'stock_volatility.png')
    plt.close()
""" based on information from https://www.visualcapitalist.com/the-global-stock-market-by-sector/
    a real breakdown of industry representation in the stock market to compare our data to"""
def plot_real_industry_stats(): 
# Create DataFrame manually
    data = {
        'Sector': ['Information Technology', 'Financials', 'Industrials', 
                'Consumer Discretionary', 'Health Care', 'Communication Services',
                'Consumer Staples', 'Energy', 'Materials', 'Utilities', 'Real Estate'],
        'Market Cap': ['$25.67T', '$21.14T', '$15.32T', '$13.66T', '$10.72T', 
                    '$9.33T', '$7.90T', '$6.75T', '$6.11T', '$3.75T', '$3.29T'],
        'Market Share': [21, 17, 12, 11, 9, 8, 6, 5, 5, 3, 3],
        'Number of Firms': [6198, 5244, 8780, 6251, 4504, 
                            2226, 3155, 1416, 6462, 910, 2664]
    }

    df = pd.DataFrame(data)

    # Set seaborn style
    sns.set_style('whitegrid')

    # Create subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 10))

    # First pie chart - Number of Companies
    ax1.pie(df['Number of Firms'], labels=df['Sector'], autopct='%1.1f%%',
            textprops={'fontsize': 9}, startangle=90)
    ax1.set_title('Distribution by Number of Companies', fontsize=14, pad=20)

    # Second pie chart - Market Share
    ax2.pie(df['Market Share'], labels=df['Sector'], autopct='%1.1f%%',
            textprops={'fontsize': 9}, startangle=90)
    ax2.set_title('Market Share Distribution', fontsize=14, pad=20)

    # Adjust layout and display
    plt.tight_layout()
    plt.savefig(output_dir / 'real_industry_stats.png')
    plt.close()

def plot_stock_industries(data):
    """Plot a detailed, labeled bar chart of stock distribution by industry."""
    industry_counts = data['Industry_Tag'].value_counts().sort_values(ascending=True)
    total = industry_counts.sum()

    # Calculate percentages
    industry_percentages = (industry_counts / total * 100).round(2)

    # Set seaborn style
    sns.set(style="whitegrid")
    fig, ax = plt.subplots(figsize=(14, max(6, len(industry_counts) * 0.4)))

    # Create horizontal bar plot
    bars = sns.barplot(
        x=industry_counts.values,
        y=industry_counts.index,
        orient='h',
        palette='viridis'
    )

    # Annotate counts and percentages
    for i, (count, pct) in enumerate(zip(industry_counts.values, industry_percentages.values)):
        ax.text(count + total * 0.01, i, f'{count} ({pct}%)', va='center', fontsize=9)

    # Set labels and title
    ax.set_title('Stock Distribution by Industry', fontsize=16, pad=15)
    ax.set_xlabel('Number of Stocks', fontsize=12)
    ax.set_ylabel('Industry Tag', fontsize=12)

    # Clean up axis
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{int(x)}'))
    ax.tick_params(axis='y', labelsize=10)
    ax.tick_params(axis='x', labelsize=10)

    # Tight layout and save
    plt.tight_layout()
    plt.savefig(output_dir / 'stock_industry_distribution.png')
    plt.close()
    print(f"✓ Saved detailed industry distribution chart to {output_dir / 'stock_industry_distribution.png'}")
def chart_all(data):
    """Plot all charts for the analysis."""
    print("Plotting all charts...")
    plot_historical_performance_per_stock(data)
    chart_volatility_per_stock(data)
    plot_stock_industries(data)
    plot_real_industry_stats()
    plot_bollinger_bands(data)

def plot_bollinger_bands(data):
    print("Plotting Bollinger Bands per stock...")

    grouped = data.groupby('Ticker')
    for ticker, group in grouped:
        group = group.sort_values('Date')
        group['MA20'] = group['Close'].rolling(window=20).mean() #20 day moving average
        group['Upper'] = group['MA20'] + 2 * group['Close'].rolling(window=20).std()
        group['Lower'] = group['MA20'] - 2 * group['Close'].rolling(window=20).std()

        plt.figure(figsize=(14, 6))
        plt.plot(group['Date'], group['Close'], label='Close Price')
        plt.plot(group['Date'], group['MA20'], label='20-day MA', linestyle='--')
        plt.plot(group['Date'], group['Upper'], label='Upper Band', linestyle='-.')
        plt.plot(group['Date'], group['Lower'], label='Lower Band', linestyle='-.')
        plt.fill_between(group['Date'], group['Upper'], group['Lower'], color='gray', alpha=0.1)

        plt.title(f'Bollinger Bands - {ticker}')
        plt.xlabel('Date')
        plt.ylabel('Price')
        plt.legend()
        plt.xticks(rotation=45)
        plt.tight_layout()

        save_path = output_dir / f'bollinger_bands_{ticker}.png'
        plt.savefig(save_path)
        plt.close()
def main():
    """Main function to run the analysis."""
    print("=== Stock Market Data Analysis ===")
    data = load_data('bin/data/stock_data.csv')
    print("Data loaded:", data.head())
    print("Columns in DataFrame:", data.columns)
    industry_tag = data['Industry_Tag'].unique()
    print("Unique Industry Tags:", industry_tag)
    print("Plotting stock industry distribution...")
    plot_stock_industries(data)
    # Plot real industry stats
    plot_real_industry_stats()
    print("\n=== Analysis completed successfully ===")


if __name__ == "__main__":
    main()