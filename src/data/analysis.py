import sys
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
import os

# Increase default figure and font sizes for readability
plt.rcParams.update({
    'figure.figsize': (16, 9),
    'font.size': 14,
    'axes.titlesize': 18,
    'axes.labelsize': 16,
    'xtick.labelsize': 14,
    'ytick.labelsize': 14,
    'legend.fontsize': 14
})



# Output directory for figures
output_dir = Path("bin/data/figs")
output_dir.mkdir(parents=True, exist_ok=True)


def plot_historical_performance_per_stock(data):
    print("Plotting historical performance of each stock...")
    tickers = data['Ticker'].unique()
    for ticker in tickers:
        stock = data[data['Ticker'] == ticker].sort_index()
        plt.figure(figsize=(18, 6))
        plt.plot(stock.index, stock['Open'], label='Open Price')
        plt.plot(stock.index, stock['Close'], label='Close Price')
        plt.title(f'Historical Open vs Close for {ticker}')
        plt.xlabel('Date')
        plt.ylabel('Price')
        plt.legend()
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(output_dir / f'historical_{ticker}.png')
        plt.close()


def chart_volatility_per_stock(data):
    print("Plotting stock volatility...")
    data = data.copy()
    data['Return'] = data.groupby('Ticker')['Close'].pct_change()
    vol = data.groupby('Ticker')['Return'].std().sort_values()

    plt.figure(figsize=(14, 8))
    sns.barplot(x=vol.values, y=vol.index, orient='h')
    plt.title('Volatility by Stock (Std Dev of Returns)')
    plt.xlabel('Volatility')
    plt.ylabel('Ticker')
    plt.tight_layout()
    plt.savefig(output_dir / 'volatility.png')
    plt.close()


def plot_return_distribution(data):
    print("Plotting return distribution for each stock...")
    data = data.copy()
    data['Return'] = data.groupby('Ticker')['Close'].pct_change()
    tickers = data['Ticker'].unique()

    for ticker in tickers:
        series = data[data['Ticker'] == ticker]['Return'].dropna()
        plt.figure(figsize=(14, 6))
        sns.histplot(series, bins=50, kde=True)
        plt.title(f'Return Distribution for {ticker}')
        plt.xlabel('Daily Return')
        plt.ylabel('Frequency')
        plt.tight_layout()
        plt.savefig(output_dir / f'return_dist_{ticker}.png')
        plt.close()


def plot_volume_trends(data):
    print("Plotting volume trends...")
    tickers = data['Ticker'].unique()
    for ticker in tickers:
        stock = data[data['Ticker'] == ticker]
        stock['Volume_MA20'] = stock['Volume'].rolling(window=20).mean()
        plt.figure(figsize=(18, 6))
        plt.plot(stock.index, stock['Volume'], alpha=0.3, label='Volume')
        plt.plot(stock.index, stock['Volume_MA20'], label='20-day MA Volume')
        plt.title(f'Volume Trend for {ticker}')
        plt.xlabel('Date')
        plt.ylabel('Volume')
        plt.legend()
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(output_dir / f'volume_trend_{ticker}.png')
        plt.close()


def plot_bollinger_bands(data):
    print("Plotting Bollinger Bands per stock...")
    for ticker, group in data.groupby('Ticker'):
        grp = group.sort_index()
        ma = grp['Close'].rolling(20).mean()
        sd = grp['Close'].rolling(20).std()
        upper, lower = ma + 2*sd, ma - 2*sd

        plt.figure(figsize=(18, 6))
        plt.plot(grp.index, grp['Close'], label='Close')
        plt.plot(grp.index, ma, label='20-day MA', linestyle='--')
        plt.fill_between(grp.index, upper, lower, color='grey', alpha=0.2, label='Bollinger Bands')
        plt.title(f'Bollinger Bands - {ticker}')
        plt.xlabel('Date')
        plt.ylabel('Price')
        plt.legend()
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(output_dir / f'bollinger_{ticker}.png')
        plt.close()


def plot_correlation_heatmap(data):
    print("Plotting correlation heatmap across tickers...")
    pivot = data.pivot_table(index='Date', columns='Ticker', values='Close')
    corr = pivot.corr()
    plt.figure(figsize=(12, 10))
    sns.heatmap(corr, annot=True, fmt='.2f', cmap='coolwarm', square=True)
    plt.title('Correlation Matrix of Close Prices')
    plt.tight_layout()
    plt.savefig(output_dir / 'correlation_heatmap.png')
    plt.close()


def main():
    print("=== Stock Market Analysis & Visualization ===")
    data = load_data('bin/data/stock_data.csv')
    data.index = pd.to_datetime(data.index)

    plot_historical_performance_per_stock(data)
    chart_volatility_per_stock(data)
    plot_return_distribution(data)
    plot_volume_trends(data)
    plot_bollinger_bands(data)
    plot_correlation_heatmap(data)

    print("=== All figures saved to", output_dir)  

if __name__ == '__main__':
    main()
