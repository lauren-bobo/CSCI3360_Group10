import os
import sys
import subprocess
import kagglehub
import pandas as pd
import numpy as np
import seaborn as sns
from pathlib import Path

def check_and_install_packages():
    """Check and install required packages if missing"""
    required_packages = ["kagglehub", "pandas", "numpy", "seaborn"]
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✓ {package} is already installed")
        except ImportError:
            print(f"Installing {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"✓ {package} installed successfully")

def setup_kaggle_auth():
    """Set up Kaggle authentication"""
    # Check if Kaggle credentials already exist in environment
    if os.environ.get('KAGGLE_USERNAME') and os.environ.get('KAGGLE_KEY'):
        print("✓ Kaggle credentials found in environment variables")
        return True
    
    # Check if kaggle.json exists
    kaggle_dir = Path.home() / '.kaggle'
    kaggle_json = kaggle_dir / 'kaggle.json'
    
    if kaggle_json.exists():
        print("✓ Kaggle credentials found in ~/.kaggle/kaggle.json")
        return True
    
    # If no credentials found, prompt user to login
    print("No Kaggle credentials found. Please follow these steps:")
    print("1. Go to https://www.kaggle.com/account")
    print("2. Scroll to API section and click 'Create New API Token'")
    print("3. Enter your Kaggle username and API key below")
    
    try:
        username = input("Kaggle Username: ")
        api_key = input("Kaggle API Key: ")
        
        # Store in environment variables for current session
        os.environ['KAGGLE_USERNAME'] = username
        os.environ['KAGGLE_KEY'] = api_key
        
        # Create .kaggle directory if it doesn't exist
        kaggle_dir.mkdir(exist_ok=True)
        
        # Save credentials to kaggle.json for future use
        with open(kaggle_json, 'w') as f:
            f.write(f'{{"username":"{username}","key":"{api_key}"}}')
        
        # Set proper permissions
        os.chmod(kaggle_json, 0o600)
        
        print(f"✓ Credentials saved to {kaggle_json}")
        return True
    except Exception as e:
        print(f"Error setting up Kaggle authentication: {e}")
        return False

def download_dataset(dataset_id, data_dir):
    """Download dataset if it doesn't exist or has updates"""
    try:
        # Ensure the data directory exists
        data_dir.mkdir(parents=True, exist_ok=True)
        
        # Download/update the dataset
        downloaded_path = kagglehub.dataset_download(
            dataset_id,
            path=str(data_dir),
            force_download=True
        )
        
        # Store the path in environment variables
        os.environ['STOCK_DATA_PATH'] = str(data_dir)
        
        print(f"✓ Dataset downloaded to: {data_dir}")
        print(f"✓ Path stored in STOCK_DATA_PATH environment variable")
        return True
    except Exception as e:
        print(f"Error downloading dataset: {e}")
        return False

def main():
    """Main function to run the data pipeline"""
    # Get the project root directory (assuming src is one level below project root)
    project_root = Path(__file__).parent.parent.parent
    data_dir = project_root / "data" / "stock_data"
    
    print("=== Stock Market Data Pipeline ===")
    
    # Set up Kaggle authentication
    print("\n[1/2] Setting up Kaggle authentication...")
    if not setup_kaggle_auth():
        print("Failed to set up Kaggle authentication. Exiting.")
        return
    
    # Download dataset
    print("\n[2/2] Downloading dataset...")
    dataset_id = "nelgiriyewithana/world-stock-prices-daily-updating"
    if not download_dataset(dataset_id, data_dir):
        print("Failed to download dataset. Exiting.")
        return
    
    print("\n=== Pipeline completed successfully ===")

if __name__ == "__main__":
    main()

