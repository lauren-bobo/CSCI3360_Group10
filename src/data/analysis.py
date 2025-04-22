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

def load_data(filepath, days=180):
    """
    Load stock data CSV, parse Date column, set as index,
    then return only the most recent `days` calendar days.
    Expects columns: Date,Open,High,Low,Close,Volume,Brand_Name,
                     Ticker,Industry_Tag,Country,Dividends,Stock Splits,Capital Gains
    """
    df = pd.read_csv(filepath, parse_dates=['Date'])
    df = df.set_index('Date').sort_index()
    cutoff = df.index.max() - pd.Timedelta(days=days)
    return df.loc[cutoff:]

def plot_historical_performance_per_stock(data):
    print("Plotting historical performance of each stock...")
    for ticker in data['Ticker'].unique():
        stock = data[data['Ticker'] == ticker]
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

def plot_facet_historical(data, tickers_per_page=9):
    print("Plotting faceted historical close prices...")
    tickers = sorted(data['Ticker'].unique())
    pages = [tickers[i:i+tickers_per_page] for i in range(0, len(tickers), tickers_per_page)]
    for page_num, page in enumerate(pages, 1):
        fig, axes = plt.subplots(3, 3, figsize=(18, 12), sharex=True, sharey=True)
        axes = axes.flatten()
        for ax, ticker in zip(axes, page):
            df_t = data[data['Ticker'] == ticker]
            ax.plot(df_t.index, df_t['Close'])
            ax.set_title(ticker)
            ax.tick_params(axis='x', rotation=30, labelsize=10)
        for ax in axes[len(page):]:
            ax.set_visible(False)
        fig.suptitle(f'Historical Close Prices (Page {page_num})', fontsize=20)
        fig.tight_layout(rect=[0, 0, 1, 0.95])
        fig.savefig(output_dir / f'historical_facet_page{page_num}.png')
        plt.close(fig)

def chart_volatility_per_stock(data):
    print("Plotting stock volatility...")
    df = data.copy()
    df['Return'] = df.groupby('Ticker')['Close'].pct_change()
    vol = df.groupby('Ticker')['Return'].std().sort_values()
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
    df = data.copy()
    df['Return'] = df.groupby('Ticker')['Close'].pct_change()
    for ticker in df['Ticker'].unique():
        series = df[df['Ticker'] == ticker]['Return'].dropna()
        plt.figure(figsize=(14, 6))
        sns.histplot(series, bins=50, kde=True)
        plt.title(f'Return Distribution for {ticker}')
        plt.xlabel('Daily Return')
        plt.ylabel('Frequency')
        plt.tight_layout()
        plt.savefig(output_dir / f'return_dist_{ticker}.png')
        plt.close()

def plot_return_boxplot(data):
    print("Plotting return boxplot across all stocks...")
    df = data.copy()
    df['Return'] = df.groupby('Ticker')['Close'].pct_change()
    df = df.dropna(subset=['Return'])
    plt.figure(figsize=(20, 8))
    sns.boxplot(x='Ticker', y='Return', data=df, showfliers=False)
    plt.xticks(rotation=90, fontsize=8)
    plt.title('Daily Return Distribution by Ticker')
    plt.xlabel('Ticker')
    plt.ylabel('Daily Return')
    plt.tight_layout()
    plt.savefig(output_dir / 'return_boxplot.png')
    plt.close()

def plot_mean_vol_scatter(data):
    print("Plotting mean vs volatility scatter...")
    df = data.copy()
    df['Return'] = df.groupby('Ticker')['Close'].pct_change()
    stats = df.groupby('Ticker')['Return'].agg(['mean', 'std']).dropna()
    plt.figure(figsize=(12, 10))
    sns.scatterplot(x='std', y='mean', data=stats)
    for ticker, row in stats.iterrows():
        plt.text(row['std'], row['mean'], ticker, fontsize=8)
    plt.xlabel('Volatility (Std Dev of Returns)')
    plt.ylabel('Mean Daily Return')
    plt.title('Mean vs. Volatility by Ticker')
    plt.tight_layout()
    plt.savefig(output_dir / 'mean_vs_volatility.png')
    plt.close()

def plot_volume_trends(data):
    print("Plotting volume trends...")
    for ticker in data['Ticker'].unique():
        stock = data[data['Ticker'] == ticker].copy()
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

def plot_volume_trends_log(data):
    print("Plotting log-scale volume trends...")
    for ticker in data['Ticker'].unique():
        stock = data[data['Ticker'] == ticker].copy()
        stock['Volume_MA20'] = stock['Volume'].rolling(window=20).mean()
        plt.figure(figsize=(18, 6))
        plt.plot(stock.index, stock['Volume_MA20'], label='20‑day MA')
        plt.yscale('log')
        plt.title(f'Log-Scale Volume Trend for {ticker}')
        plt.xlabel('Date')
        plt.ylabel('Volume (log scale)')
        plt.legend()
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(output_dir / f'volume_log_{ticker}.png')
        plt.close()

def plot_bollinger_bands(data):
    print("Plotting Bollinger Bands per stock...")
    for ticker, group in data.groupby('Ticker'):
        grp = group
        ma = grp['Close'].rolling(20).mean()
        sd = grp['Close'].rolling(20).std()
        upper, lower = ma + 2*sd, ma - 2*sd
        plt.figure(figsize=(18, 6))
        plt.plot(grp.index, grp['Close'], label='Close')
        plt.plot(grp.index, ma, label='20-day MA', linestyle='--')
        plt.fill_between(grp.index, upper, lower, alpha=0.2, label='Bollinger Bands')
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
    pivot = data.pivot_table(index=data.index, columns='Ticker', values='Close')
    corr = pivot.corr()
    plt.figure(figsize=(12, 10))
    sns.heatmap(corr, annot=True, fmt='.2f', cmap='coolwarm', square=True)
    plt.title('Correlation Matrix of Close Prices')
    plt.tight_layout()
    plt.savefig(output_dir / 'correlation_heatmap.png')
    plt.close()

def plot_correlation_clustermap(data):
    print("Plotting clustered correlation heatmap...")
    pivot = data.pivot_table(index=data.index, columns='Ticker', values='Close')
    corr = pivot.corr()
    cg = sns.clustermap(
        corr, figsize=(14, 14), method='average',
        cmap='vlag', linewidths=0.5,
        cbar_pos=(0.02, 0.8, 0.05, 0.18),
        xticklabels=True, yticklabels=True
    )
    cg.ax_heatmap.set_xticklabels(
        cg.ax_heatmap.get_xmajorticklabels(), rotation=90, fontsize=6
    )
    cg.ax_heatmap.set_yticklabels(
        cg.ax_heatmap.get_ymajorticklabels(), rotation=0, fontsize=6
    )
    plt.suptitle('Hierarchically Clustered Correlation of Close Prices', y=1.02)
    plt.savefig(output_dir / 'correlation_clustermap.png', bbox_inches='tight')
    plt.close()

def plot_industry_pie(data):
    print("Plotting industry distribution pie chart...")
    counts = data['Industry_Tag'].value_counts()
    plt.figure(figsize=(16, 16))
    wedges, texts, autotexts = plt.pie(
        counts.values,
        labels=counts.index,
        autopct='%1.1f%%',
        startangle=90,
        textprops={'fontsize': 12}
    )
    # make label text even bigger and bolder
    for t in texts:
        t.set_fontsize(14)
        t.set_weight('bold')
    for a in autotexts:
        a.set_fontsize(12)
    plt.title('Industry Distribution (Last 180 Days)', fontsize=16, weight='bold')
    plt.tight_layout()
    plt.savefig(output_dir / 'industry_distribution_pie.png')
    plt.close()


def main():
    print("=== Stock Market Analysis & Visualization (Last 180 Days) ===")
    data = load_data('bin/data/stock_data.csv', days=180)
    plot_industry_pie(data)
    """plot_historical_performance_per_stock(data)
    plot_facet_historical(data)
    chart_volatility_per_stock(data)
    plot_return_distribution(data)
    plot_return_boxplot(data)
    plot_mean_vol_scatter(data)
    plot_volume_trends(data)
    plot_volume_trends_log(data)
    plot_bollinger_bands(data)
    plot_correlation_heatmap(data)
    plot_correlation_clustermap(data)"""




    print("=== All figures (180d) saved to", output_dir)


if __name__ == '__main__':
    main()