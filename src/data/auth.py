import os
import json
from pathlib import Path
from typing import Optional, Dict

class KaggleAuth:
    def __init__(self):
        self.kaggle_dir = Path.home() / '.kaggle'
        self.kaggle_json = self.kaggle_dir / 'kaggle.json'

    def is_authenticated(self) -> bool:
        """Check if Kaggle credentials file exists"""
        return self.kaggle_json.exists()

    def setup(self) -> bool:
        """Set up Kaggle authentication by storing token file"""
        if self.is_authenticated():
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
            self.kaggle_dir.mkdir(exist_ok=True)
            
            # Copy the token file to .kaggle directory
            with open(token_path, 'r') as source:
                credentials = json.load(source)
                
            with open(self.kaggle_json, 'w') as target:
                json.dump(credentials, target)
                
            # Set proper permissions
            os.chmod(self.kaggle_json, 0o600)
            
            print(f"✓ Token file copied to {self.kaggle_json}")
            return True
            
        except Exception as e:
            print(f"Error setting up Kaggle authentication: {e}")
            return False 