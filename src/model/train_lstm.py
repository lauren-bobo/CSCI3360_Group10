import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler 
from sklearn.model_selection import train_test_split
import tensorflow as tf
from keras.models import Sequential
from keras.layers import LSTM, Dense, Dropout
"""Not Yet Functional, for data formatting only: Train an LSTM model for stock price prediction."""
def build_model():
    """Build and compile the LSTM model."""
    model = Sequential()
    model.add(LSTM(units=50, return_sequences=True, input_shape=(60, 1)))
    model.add(Dropout(0.2))
    model.add(LSTM(units=50, return_sequences=False))
    model.add(Dropout(0.2))
    model.add(Dense(units=1))  # Output layer
    model.compile(optimizer='adam', loss='mean_squared_error')
    return model

def prepare_for_model(data):
    """Prepare the data for LSTM model."""
    # Ensure data is a DataFrame
    if isinstance(data, tuple):
        print("Warning: Data is a tuple, extracting DataFrame.")
        data = data[0]  # Assuming the first element is the DataFrame

    # Check if 'Close' column exists
    if 'Close' not in data.columns:
        raise KeyError("The 'Close' column is missing from the data.")

    # Scale the data
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(data[['Close']].values)

    # Create sequences
    X, y = [], []
    for i in range(60, len(scaled_data)):
        X.append(scaled_data[i-60:i, 0])  # Previous 60 days
        y.append(scaled_data[i, 0])       # Current day

    X, y = np.array(X), np.array(y)
    X = X.reshape((X.shape[0], X.shape[1], 1))  # Reshape for LSTM
    return X, y, scaler

def main(data):
    """Main function to run the LSTM training."""
    # Ensure data is a DataFrame
    if isinstance(data, tuple):
        print("Warning: Data is a tuple, extracting DataFrame.")
        data = data[0]  # Assuming the first element is the DataFrame

    # Prepare the data
    X, y, scaler = prepare_for_model(data)

    # Build the model
    model = build_model()

    # Train the model
    model.fit(X, y, epochs=50, batch_size=32)

    # Save the model if needed
    model.save('lstm_model.h5')

    print(tf.__version__)

def run():
    """Run the LSTM training process."""
    # Load the data (assuming the data is already prepared and passed)
    data = pd.read_csv('bin/data/stock_data.csv')  # Adjust the path as necessary
    main(data)  # Call the main function to train the model

if __name__ == "__main__":
    run()