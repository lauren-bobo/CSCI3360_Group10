import os
import kagglehub
from pathlib import Path
import pandas as pd
import json
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from datetime import timedelta
"""NOT YET WORKING, PURELY TO FORMAT INPUT DATA FOR LSTM""" 
# Configuration file in project root
CONFIG_FILE = "config.json"

def save_last_n_days_to_csv(file_path, n):
    """Load CSV, filter last n days, and overwrite the file."""
    data = pd.read_csv(file_path)
    data['Date'] = pd.to_datetime(data['Date'], errors='coerce', utc=True)

    # Filter the last n days
    max_date = data['Date'].max()
    cutoff_date = max_date - timedelta(days=n)
    filtered_data = data[data['Date'] >= cutoff_date]

    # Overwrite the file
    filtered_data.to_csv(file_path, index=False)
    print(f"✓ Overwrote {file_path} with last {n} days of data ({cutoff_date.date()} - {max_date.date()})")


def load_config():
    """Load configuration from file or create default"""
    if Path(CONFIG_FILE).exists():
        with open(CONFIG_FILE, 'r') as file:
            return json.load(file)
    
    # Default configuration
    default_config = {
        "kaggle": {},
        "paths": {
            "data_dir": "bin/data",
            "output_file": "bin/data/stock_data.csv"
        },
        "dataset": {
            "id": "nelgiriyewithana/world-stock-prices-daily-updating",
            "version": None  # Placeholder for dataset version
        }
    }
    
    # Save default config
    with open(CONFIG_FILE, 'w') as file:
        json.dump(default_config, file, indent=2)
    
    return default_config

def save_config(config):
    """Save configuration to file"""
    with open(CONFIG_FILE, 'w') as file:
        json.dump(config, file, indent=2)

def setup_kaggle_auth():
    """Authenticate with Kaggle"""
    config = load_config()
    
    # Check if credentials exist in config
    if 'username' in config.get('kaggle', {}) and 'api_key' in config.get('kaggle', {}):
        os.environ['KAGGLE_USERNAME'] = config['kaggle']['username']
        os.environ['KAGGLE_KEY'] = config['kaggle']['api_key']
        print("✓ Using stored Kaggle credentials")
        return True

    # Prompt user for credentials if not found
    print("Kaggle credentials not found. Please enter your credentials.")
    username = input("Enter your Kaggle username: ")
    api_key = input("Enter your Kaggle API key: ")

    # Store credentials in the config
    config['kaggle']['username'] = username
    config['kaggle']['api_key'] = api_key
    save_config(config)

    # Set environment variables
    os.environ['KAGGLE_USERNAME'] = username
    os.environ['KAGGLE_KEY'] = api_key

    print("✓ Kaggle credentials saved. Ensure Proper setup in ~/config")
    return True

def download_and_save_dataset(dataset_id, file_name):
    """Download dataset and save to configured location"""
    config = load_config()
    
    # Get paths from config
    output_file = config['paths']['output_file']
    
    # Create directories if they don't exist
    Path(output_file).parent.mkdir(parents=True, exist_ok=True)
    
    try:
        # Download the dataset without specifying a path
        download_path = kagglehub.dataset_download(
            dataset_id,
            force_download=True
        )
        
        print(f"✓ Dataset downloaded to: {download_path}")
        
        # Load the downloaded file into a DataFrame
        try:
            df = pd.read_csv(Path(download_path) / file_name)
            
            print(f"Saving dataset to: {output_file}")  # Debugging line
            df.to_csv(output_file, index=False)
            print(f"✓ Dataset processed and saved to: {output_file}")
        except FileNotFoundError:
            print(f"Warning: Could not find {file_name} in the downloaded dataset.")
            print(f"Available files: {os.listdir(download_path)}")
            return False
        
        return True
    except Exception as e:
        print(f"Error downloading or processing dataset: {e}")
        print(f"Exception details: {type(e).__name__}: {str(e)}")
        return False

def load_data(file):
    data = pd.read_csv(file)
    data = pd.DataFrame(data)
    data['Date'] = pd.to_datetime(data['Date'], utc=True)

    # Print the columns to check for 'Stock'
    print("Data loaded:", data.head())  # Print the first few rows of the data
    print("Columns in DataFrame:", data.columns)  # Print the columns to check for 'Stock'

    # Strip whitespace from column names
    data.columns = data.columns.str.strip()


    return data

def replace_Industry_Tag_with_sector(data):
    industry_tag = data['Industry_Tag'].unique()
    print("Unique Industry Tags:", industry_tag)
    # Replace 'Industry_Tag' with 'Sector'
    

def prepare_data(data):
    """Prepare the data for LSTM model with multiple stocks."""
    # Convert 'Date' to datetime
    data['Date'] = pd.to_datetime(data['Date'], errors='coerce', utc=True)  # Convert to datetime and localize to UTC

    # Check for any NaT values after conversion
    if data['Date'].isnull().any():
        print("Warning: Some dates could not be converted and are NaT.")
        print(data[data['Date'].isnull()])  # Print rows with NaT values

    data.set_index('Date', inplace=True)

    # Group by Ticker instead of Stock
    grouped = data.groupby('Ticker')

    X, y, scalers = [], [], {}
    
    for ticker, group in grouped:
        # Scale the data for each ticker
        scaler = MinMaxScaler(feature_range=(0, 1))
        scaled_data = scaler.fit_transform(group[['Close']])
        scalers[ticker] = scaler  # Store the scaler for inverse transformation

        # Create sequences
        for i in range(60, len(scaled_data)):
            X.append(scaled_data[i-60:i, 0])  # Previous 60 days
            y.append(scaled_data[i, 0])       # Current day

    return np.array(X), np.array(y), scalers

def main():
    """Main function to run the data pipeline."""
    print("=== Stock Market Data Pipeline ===")
    
    print("\n[1/2] Setting up Kaggle authentication...")
    if not setup_kaggle_auth():
        print("Failed to set up Kaggle authentication. Exiting.")
        return
    
    print("\n[2/2] Downloading and saving dataset...")
    dataset_id = "nelgiriyewithana/world-stock-prices-daily-updating"
    file_name = "World-Stock-Prices-Dataset.csv"
    if not download_and_save_dataset(dataset_id, file_name):
        print("Failed to download and save dataset. Exiting.")
        return

    config = load_config()
    output_path = config['paths']['output_file']
    
    save_last_n_days_to_csv(output_path, 180)

    data = load_data(output_path)
                
    print("\n=== Pipeline completed successfully ===")



if __name__ == "__main__":
    main()