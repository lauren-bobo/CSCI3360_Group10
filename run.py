import os
import sys
from pathlib import Path
from sklearn.model_selection import train_test_split
# Set the PYTHONPYCACHEPREFIX to redirect __pycache__ to bin/pycache
os.environ['PYTHONPYCACHEPREFIX'] = str(Path(__file__).parent / 'bin' / 'pycache')

# Add src directory to path so we can import from itls -
sys.path.append(str(Path(__file__).parent))

from src.data.API.pipeline import setup_kaggle_auth, download_and_save_dataset, load_config, load_data, prepare_data
from src.data.analysis import chart_all
from src.model.train_lstm import main as train_lstm_main, run  # Import both main and run functions

def main():
    """Main function to run the data pipeline."""
    
    print("Welcome To The stock prediction model:")
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
    data = load_data('bin\data\stock_data.csv')  
    chart_all(data)  
    
    print("\n[3/3] Training LSTM models...")
    # Run the LSTM training
    run()  # This will train models for all stocks and save them

    print("\n=== Pipeline completed successfully ===")

if __name__ == "__main__":
    main()