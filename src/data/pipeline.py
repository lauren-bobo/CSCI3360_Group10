import os
import kagglehub
from pathlib import Path
import pandas as pd
import json

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
            "data_dir": "data",
            "output_file": "data/stock_data.csv"
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

    try:
        # Try to authenticate with kagglehub
        kagglehub.login()
        print("✓ Kaggle authentication successful")
        
        # Store credentials if available
        username = os.environ.get('KAGGLE_USERNAME')
        api_key = os.environ.get('KAGGLE_KEY')
        
        if username and api_key:
            if 'kaggle' not in config:
                config['kaggle'] = {}
            config['kaggle']['username'] = username
            config['kaggle']['api_key'] = api_key
            save_config(config)
            print("✓ Credentials saved to config file")
        
        return True
    except Exception as e:
        print(f"Error during Kaggle authentication: {e}")
        return False

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
            
            # Save to the configured output location
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

def main():
    """Main function to run the data pipeline."""
    print("=== Stock Market Data Pipeline ===")
    
    print("\n[1/2] Setting up Kaggle authentication...")
    if not setup_kaggle_auth():
        print("Failed to set up Kaggle authentication. Exiting.")
        return
    
    print("\n[2/2] Downloading and saving dataset...")
    dataset_id = "nelgiriyewithana/world-stock-prices-daily-updating"
    file_name = "your_dataset_file.csv"  # Replace with the actual file name
    if not download_and_save_dataset(dataset_id, file_name):
        print("Failed to download and save dataset. Exiting.")
        return
    
    print("\n=== Pipeline completed successfully ===")

if __name__ == "__main__":
    main() 