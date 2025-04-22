import os
import glob
from datetime import timedelta

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import load_model
from tabulate import tabulate

# Configuration
LOOK_BACK = 60
MODEL_DIR = "models"
DATA_PATH = "bin/data/stock_data.csv"
FIG_DIR = "results/figs"
TABLE_DIR = "results"

os.makedirs(FIG_DIR, exist_ok=True)
os.makedirs(TABLE_DIR, exist_ok=True)

# Global seaborn style and matplotlib rc for presentation
sns.set_style('whitegrid')
plt.rcParams.update({
    'figure.dpi': 200,
    'axes.titlesize': 20,
    'axes.labelsize': 18,
    'xtick.labelsize': 14,
    'ytick.labelsize': 14,
    'legend.fontsize': 16,
    'font.family': 'sans-serif',
    'font.size': 16
})

def prepare_for_model(df):
    """
    Given a DataFrame for one ticker, return train/test sequences and scaler.
    """
    df = df.sort_values('Date').reset_index(drop=True)
    scaler = MinMaxScaler()
    scaled_close = scaler.fit_transform(df[['Close']].values)

    X, y = [], []
    for i in range(LOOK_BACK, len(scaled_close)):
        X.append(scaled_close[i-LOOK_BACK:i, 0])
        y.append(scaled_close[i, 0])
    X = np.array(X).reshape(-1, LOOK_BACK, 1)
    y = np.array(y)

    split = int(0.8 * len(X))
    return X[:split], X[split:], y[:split], y[split:], scaler, df['Date'].iloc[LOOK_BACK:].reset_index(drop=True)


def forecast_next_day(df, model, scaler):
    """
    Forecast the next day's Close using the last LOOK_BACK window.
    """
    scaled = scaler.transform(df[['Close']].values)
    window = scaled[-LOOK_BACK:].reshape(1, LOOK_BACK, 1)
    pred = model.predict(window)
    return scaler.inverse_transform(pred)[0][0]


def plot_accuracy_direction(results_df, hist_df):
    """
    Plot a large, presentation-ready figure of accuracy with arrows.
    """
    # Compute previous close for each ticker
    prev = hist_df.sort_values('Date').groupby('Ticker')['Close'].last().reset_index()
    prev.columns = ['Ticker', 'Prev_Close']
    df = results_df.merge(prev, on='Ticker')
    df['Direction'] = np.where(df['Next Day Pred'] > df['Prev_Close'], '↑', '↓')

    # Sort by accuracy ascending so highest at top
    df_sorted = df.sort_values('Accuracy', ascending=True)

    # Create figure
    fig, ax = plt.subplots(figsize=(12, 18))
    sns.barplot(x='Accuracy', y='Ticker', data=df_sorted, palette='mako', ax=ax)

    # Annotate arrows with larger font
    for i, (_, row) in enumerate(df_sorted.iterrows()):
        ax.text(row['Accuracy'] + 0.01, i, row['Direction'], va='center', fontsize=20, fontweight='bold')

    ax.set_xlim(0, 1)
    ax.set_title("Model Accuracy with Predicted Direction", pad=20)
    ax.set_xlabel("Accuracy")
    ax.set_ylabel("")
    plt.tight_layout()
    fig.savefig(os.path.join(FIG_DIR, 'accuracy_with_direction_presentation.png'), dpi=200)
    plt.close(fig)


def main():
    # Load data
    data = pd.read_csv(DATA_PATH, parse_dates=['Date'])

    # Storage for metrics
    metrics = []
    mses = {}

    # Loop over models
    for model_file in glob.glob(os.path.join(MODEL_DIR, "lstm_*.h5")):
        ticker = os.path.basename(model_file).split('_')[1].split('.')[0]
        df_t = data[data['Ticker'] == ticker].copy()
        if len(df_t) < LOOK_BACK * 2:
            continue

        X_train, X_test, y_train, y_test, scaler, dates = prepare_for_model(df_t)
        model = load_model(model_file)

        train_preds = model.predict(X_train)
        test_preds = model.predict(X_test)

        train_act = scaler.inverse_transform(train_preds)
        train_y_act = scaler.inverse_transform(y_train.reshape(-1, 1))
        test_act = scaler.inverse_transform(test_preds)
        test_y_act = scaler.inverse_transform(y_test.reshape(-1, 1))

        mse_test = np.mean((test_act - test_y_act) ** 2)
        mses[ticker] = mse_test

        next_date = df_t['Date'].max() + timedelta(days=1)
        next_pred = forecast_next_day(df_t, model, scaler)

        metrics.append({
            'Ticker': ticker,
            'Test MSE': mse_test,
            'Next Date': next_date.date(),
            'Next Day Pred': round(next_pred, 2)
        })

        # Plot actual vs predicted per ticker (presentation-ready)
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.lineplot(x=dates.iloc[:len(train_y_act)], y=train_y_act.flatten(), label='Train Actual', ax=ax)
        sns.lineplot(x=dates.iloc[:len(train_act)], y=train_act.flatten(), label='Train Pred', ax=ax)
        sns.lineplot(x=dates.iloc[len(train_y_act):], y=test_y_act.flatten(), label='Test Actual', ax=ax)
        sns.lineplot(x=dates.iloc[len(train_act):], y=test_act.flatten(), label='Test Pred', ax=ax)
        ax.set_title(f"{ticker} Actual vs Predicted", pad=12)
        ax.set_xlabel('Date')
        ax.set_ylabel('Close Price')
        plt.xticks(rotation=45)
        plt.tight_layout()
        fig.savefig(os.path.join(FIG_DIR, f"predictions_{ticker}_presentation.png"), dpi=200)
        plt.close(fig)

    # Overall MSE bar (presentation)
    mse_df = pd.DataFrame(list(mses.items()), columns=['Ticker', 'Test MSE']).sort_values('Test MSE')
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.barplot(data=mse_df, x='Ticker', y='Test MSE', palette='viridis', ax=ax)
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right')
    ax.set_title('Test MSE by Ticker', pad=12)
    plt.tight_layout()
    fig.savefig(os.path.join(FIG_DIR, 'mse_overall_presentation.png'), dpi=200)
    plt.close(fig)

    # Results table
    results_df = pd.DataFrame(metrics).sort_values('Test MSE')
    results_df['Accuracy'] = (1 / (1 + results_df['Test MSE'])).round(4)
    print(tabulate(results_df, headers='keys', tablefmt='grid', showindex=False))
    results_df.to_csv(os.path.join(TABLE_DIR, 'model_performance.csv'), index=False)

    # Presentation-ready accuracy figure
    plot_accuracy_direction(results_df, data)

    print(f"\nPresentation figures saved to {FIG_DIR}/ and table saved to {TABLE_DIR}/model_performance.csv")

if __name__ == '__main__':
    main()