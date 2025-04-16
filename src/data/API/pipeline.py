import os
import kagglehub
from pathlib import Path
import pandas as pd
import json
import numpy as np
from sklearn.preprocessing import MinMaxScaler
"""NOT YET WORKING, PURELY TO FORMAT INPUT DATA FOR LSTM""" 
# Configuration file in project root
CONFIG_FILE = "config.json"

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
    """Load data from CSV file and ensure proper date handling."""
    # Read CSV with specific column types
    data = pd.read_csv(file, dtype={
        'Date': str,
        'Open': float,
        'High': float,
        'Low': float,
        'Close': float,
        'Volume': float,
        'Brand_Name': str,
        'Ticker': str,
        'Industry_Tag': str,
        'Country': str,
        'Dividends': float,
        'Stock Splits': float,
        'Capital Gains': float
    })
    
    # Convert 'Date' to datetime while preserving timezone information
    data['Date'] = pd.to_datetime(data['Date'])
    
    # Print data info for debugging
    print("\nDataset Info:")
    print(f"Total rows: {len(data)}")
    print(f"Unique stocks: {data['Ticker'].nunique()}")
    print(f"Date range: {data['Date'].min()} to {data['Date'].max()}")
    
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
def drop_data_for_lstm(data, days):
    """Drop data for LSTM model based on the specified number of days."""
    if days not in [30, 90]:
        raise ValueError("Days must be either 30 or 90.")
    
    # Ensure the date index is timezone-aware and in UTC
    if data.index.tz is None:
        data.index = data.index.tz_localize('UTC')
    elif data.index.tz.zone != 'UTC':
        data.index = data.index.tz_convert('UTC')
    
    # Calculate the cutoff date
    current_date = pd.Timestamp.now(tz='UTC')
    cutoff_date = current_date - pd.Timedelta(days=days)
    
    # Drop rows where the date is less than the cutoff date
    filtered_data = data[data.index >= cutoff_date]
    
    print(f"Data filtered to include only the last {days} days")
    print(f"Date range: {filtered_data.index.min()} to {filtered_data.index.max()}")
    return filtered_data

def validate_dates(data):
    """Validate that dates are properly formatted and in chronological order."""
    # Ensure timezone awareness
    if data.index.tz is None:
        print("Warning: Dates were timezone-naive. Converting to UTC...")
        data.index = data.index.tz_localize('UTC')
    
    # Check for missing dates
    if data.index.isnull().any():
        print("Warning: Found missing dates in the data")
        data = data.dropna(subset=[data.index.name])
    
    # Check for duplicate dates
    if data.index.duplicated().any():
        print("Warning: Found duplicate dates in the data")
        data = data[~data.index.duplicated(keep='first')]
    
    # Ensure dates are sorted
    if not data.index.is_monotonic_increasing:
        print("Warning: Dates were not in chronological order. Sorting data...")
        data.sort_index(inplace=True)
    
    return data

def validate_stock_data(data):
    """Validate the stock data format and content."""
    required_columns = [
        'Date', 'Open', 'High', 'Low', 'Close', 'Volume',
        'Brand_Name', 'Ticker', 'Industry_Tag', 'Country'
    ]
    
    # Check for required columns
    missing_cols = [col for col in required_columns if col not in data.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")
    
    # Check for null values in critical columns
    critical_cols = ['Date', 'Close', 'Ticker']
    null_counts = data[critical_cols].isnull().sum()
    if null_counts.any():
        print("Warning: Null values found in critical columns:")
        print(null_counts[null_counts > 0])
    
    # Check for invalid prices
    if (data['Close'] <= 0).any():
        print("Warning: Invalid (zero or negative) closing prices found")
    
    return data

def get_stock_summary(data):
    """Generate a summary of the stock data."""
    summary = {
        'total_stocks': data['Ticker'].nunique(),
        'total_records': len(data),
        'industries': data['Industry_Tag'].unique().tolist(),
        'countries': data['Country'].unique().tolist(),
        'date_range': (data['Date'].min(), data['Date'].max())
    }
    
    print("\nStock Data Summary:")
    print(f"Total stocks: {summary['total_stocks']}")
    print(f"Total records: {summary['total_records']}")
    print(f"Industries: {len(summary['industries'])}")
    print(f"Countries: {len(summary['countries'])}")
    print(f"Date range: {summary['date_range'][0]} to {summary['date_range'][1]}")
    
    return summary

def process_stock_data(file_path):
    """Process the stock data file and return validated data."""
    # Load the data
    data = load_data(file_path)
    
    # Validate the data
    data = validate_stock_data(data)
    
    # Get summary
    summary = get_stock_summary(data)
    
    # Convert dates to UTC and set as index
    data['Date'] = pd.to_datetime(data['Date']).dt.tz_convert('UTC')
    data.set_index('Date', inplace=True)
    
    return data, summary

def main():
    """Main function to run the data pipeline."""
    print("=== Stock Market Data Pipeline ===")
    
    print("\n[1/2] Setting up Kaggle authentication...")
    if not setup_kaggle_auth():
        print("Failed to set up Kaggle authentication. Exiting.")
        return
    
    print("\n[2/2] Downloading and saving dataset...")
    dataset_id = "nelgiriyewithana/world-stock-prices-daily-updating"
    file_name = "World-Stock-Prices-Dataset.csv"  # Replace with the actual file name
    if not download_and_save_dataset(dataset_id, file_name):
        print("Failed to download and save dataset. Exiting.")
        return
    
    data = load_data('bin/data/stock_data.csv')
                
    print("\n=== Pipeline completed successfully ===")

if __name__ == "__main__":
    main() 