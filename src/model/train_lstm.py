import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import tensorflow as tf
from keras.models import Sequential
from keras.layers import LSTM, Dense, Dropout
import os
from concurrent.futures import ProcessPoolExecutor

def build_model():
    model = Sequential()
    model.add(LSTM(units=50, return_sequences=True, input_shape=(60, 1)))
    model.add(Dropout(0.2))
    model.add(LSTM(units=50, return_sequences=False))
    model.add(Dropout(0.2))
    model.add(Dense(units=1))
    model.compile(optimizer='adam', loss='mean_squared_error')
    return model

def prepare_for_model(data):
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(data[['Close']].values)

    X, y = [], []
    for i in range(60, len(scaled_data)):
        X.append(scaled_data[i-60:i, 0])
        y.append(scaled_data[i, 0])
    X, y = np.array(X), np.array(y)
    X = X.reshape((X.shape[0], X.shape[1], 1))

    split_index = int(0.8 * len(X))
    return X[:split_index], X[split_index:], y[:split_index], y[split_index:], scaler

def train_single_stock(stock_data, ticker):
    try:
        stock_data = stock_data.sort_values('Date')
        if len(stock_data) < 120:
            return f"Skipping {ticker} (not enough data)"

        X_train, X_test, y_train, y_test, scaler = prepare_for_model(stock_data)

        model = build_model()
        model.fit(X_train, y_train, epochs=50, batch_size=32, validation_data=(X_test, y_test), verbose=0)

        predictions = model.predict(X_test)
        predictions_actual = scaler.inverse_transform(predictions)
        y_test_actual = scaler.inverse_transform(y_test.reshape(-1, 1))

        mse = np.mean((predictions_actual - y_test_actual) ** 2)

        os.makedirs("models", exist_ok=True)
        model.save(f"models/lstm_{ticker}.h5")

        results = [f"{ticker} MSE: {mse:.2f}"]
        for i in range(min(5, len(predictions_actual))):
            results.append(f"Predicted: {predictions_actual[i][0]:.2f}, Actual: {y_test_actual[i][0]:.2f}")
        return "\n".join(results)

    except Exception as e:
        return f"Error training {ticker}: {e}"

def run():
    data = pd.read_csv("bin/data/stock_data.csv")
    tickers = data['Ticker'].unique()

    tasks = []
    with ProcessPoolExecutor() as executor:
        for ticker in tickers:
            stock_data = data[data['Ticker'] == ticker].copy()
            tasks.append(executor.submit(train_single_stock, stock_data, ticker))

        for future in tasks:
            result = future.result()
            print("\n" + result)

if __name__ == "__main__":
    run()
