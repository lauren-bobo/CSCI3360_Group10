import os
import sys
from pathlib import Path

# Set the PYTHONPYCACHEPREFIX to redirect __pycache__ to bin/pycache
os.environ['PYTHONPYCACHEPREFIX'] = str(Path(__file__).parent / 'bin' / 'pycache')

# Add src directory to path so we can import from it
sys.path.append(str(Path(__file__).parent))

from src.data.pipeline import setup_kaggle_auth, download_and_save_dataset, load_config

def main():
    """Main function to run the data pipeline."""
    print("=== Stock Market Data Pipeline ===")
    
    # Load configuration
    config = load_config()
    
    print("\n[1/2] Setting up Kaggle authentication...")
    if not setup_kaggle_auth():
        print("Failed to set up Kaggle authentication. Exiting.")
        return
    
    print("\n[2/2] Downloading and saving dataset...")
    dataset_id = "nelgiriyewithana/world-stock-prices-daily-updating"
    
    # Try to find the correct file name
    try:
        import kagglehub
        import os
        
        # Download dataset metadata to check available files
        temp_path = kagglehub.dataset_download(
            dataset_id,
            force_download=False
        )
        
        # List available files
        files = os.listdir(temp_path)
        csv_files = [f for f in files if f.endswith('.csv')]
        
        if csv_files:
            file_name = csv_files[0]  # Use the first CSV file
            print(f"Found dataset file: {file_name}")
        else:
            file_name = "stock_prices.csv"  # Default fallback
            print(f"No CSV files found, using default name: {file_name}")
    except Exception:
        file_name = "stock_prices.csv"  # Default fallback
        print(f"Using default file name: {file_name}")
    
    if not download_and_save_dataset(dataset_id, file_name):
        print("Failed to download and save dataset. Exiting.")
        return
    
    print("\n=== Pipeline completed successfully ===")

if __name__ == "__main__":
    main() 