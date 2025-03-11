from pathlib import Path
import os
import json
import kagglehub
from pipeline import StockDataPipeline

def setup_kaggle():
    """Set up Kaggle token file"""
    kaggle_json = Path.home() / '.kaggle' / 'kaggle.json'
    
    if kaggle_json.exists():
        print("✓ Kaggle token file already exists")
        return True

    print("\nNo Kaggle token file found. Please follow these steps:")
    print("1. Go to https://www.kaggle.com/account")
    print("2. Scroll to API section and click 'Create New API Token'")
    print("3. Download the kaggle.json file")
    print("4. Enter the path to your downloaded kaggle.json file:")
    
    try:
        token_path = input("Path to kaggle.json: ").strip()
        token_path = Path(token_path).expanduser()
        
        if not token_path.exists():
            print(f"Error: File not found at {token_path}")
            return False
            
        # Create .kaggle directory if it doesn't exist
        kaggle_json.parent.mkdir(exist_ok=True)
        
        # Copy the token file
        with open(token_path, 'r') as source:
            credentials = json.load(source)
        with open(kaggle_json, 'w') as target:
            json.dump(credentials, target)
            
        os.chmod(kaggle_json, 0o600)
        return True
    except Exception as e:
        print(f"Error setting up Kaggle token: {e}")
        return False

def download_dataset():
    """Download the dataset"""
    data_dir = Path("data")
    dataset_id = "nelgiriyewithana/world-stock-prices-daily-updating"
    
    try:
        data_dir.mkdir(exist_ok=True)
        downloaded_path = kagglehub.dataset_download(
            dataset_id,
            path=str(data_dir),
            force_download=True
        )
        os.environ['STOCK_DATA_PATH'] = str(data_dir)
        print(f"✓ Dataset downloaded to: {data_dir}")
        return True
    except Exception as e:
        print(f"Error downloading dataset: {e}")
        return False

def main():
    """Main function to run the authentication and data pipeline"""
    # Get the project root directory
    project_root = Path(__file__).parent.parent.parent
    data_dir = project_root / "data" / "stock_data"
    
    # Initialize authentication and pipeline
    auth = KaggleAuth()
    pipeline = StockDataPipeline(data_dir)
    
    # Run authentication
    print("=== Checking Authentication ===")
    auth_status = auth.setup()
    
    # Run pipeline if authenticated
    if auth_status:
        pipeline.run(auth_status)
    else:
        print("Failed to authenticate. Pipeline cannot proceed.")

if __name__ == "__main__":
    main() 