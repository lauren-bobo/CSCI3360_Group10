import os
import sys
from pathlib import Path

# Set the PYTHONPYCACHEPREFIX to redirect __pycache__ to bin/pycache
os.environ['PYTHONPYCACHEPREFIX'] = str(Path(__file__).parent / 'bin' / 'pycache')

# Add src directory to path so we can import from it
sys.path.append(str(Path(__file__).parent))

from src.data.pipeline import setup_kaggle_auth, download_and_save_dataset, load_config, plot_historical_performance_per_stock, load_data

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
    
    # Load the data from the specified path
    data, grouped_data = load_data('bin/data/stock_data.csv')  # Ensure this path is correct
    plot_historical_performance_per_stock(grouped_data)  # Plot the historical performance
    print("\n=== Pipeline completed successfully ===")

if __name__ == "__main__":
    main() 