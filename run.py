import os
import sys
from pathlib import Path
import time
from datetime import datetime

# Set the PYTHONPYCACHEPREFIX to redirect __pycache__ to bin/pycache
os.environ['PYTHONPYCACHEPREFIX'] = str(Path(__file__).parent / 'bin' / 'pycache')

# Add src directory to path so we can import from it
sys.path.append(str(Path(__file__).parent))

from src.data.API.pipeline import main as data_pipeline_main
from src.data.analysis import main as chart_data_main
from src.model.train_lstm import run as train_lstm_main
from src.model.analysis import main as analyze_model_main

def clear_screen():
    """Clear the console screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    """Print the application header."""
    clear_screen()
    print("=" * 60)
    print("           STOCK MARKET PREDICTION LSTM")
    print("=" * 60)
    print(f"Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

def print_menu():
    """Print the main menu options."""
    print("\nMAIN MENU:")
    print("1. Check for data updates")
    print("2. Chart data")
    print("3. Train model")
    print("4. Analyze model")
    print("5. Exit")
    print("\nEnter your choice (1-5): ", end="")

def check_data_updates():
    """Run the data pipeline to check for updates."""
    print("\n[1/1] Checking for data updates...")
    data_pipeline_main()
    input("\nPress Enter to continue...")

def chart_data():
    """Run the data visualization process."""
    print("\n[1/1] Generating data charts...")
    chart_data_main()
    input("\nPress Enter to continue...")

def train_model():
    """Run the LSTM model training process."""
    print("\n[1/1] Training LSTM models...")
    train_lstm_main()
    input("\nPress Enter to continue...")

def analyze_model():
    """Run the model analysis process."""
    print("\n[1/1] Analyzing model performance...")
    analyze_model_main()
    input("\nPress Enter to continue...")

def main():
    """Main function to run the interactive menu."""
    while True:
        print_header()
        print_menu()
        
        choice = input()
        
        if choice == '1':
            check_data_updates()
        elif choice == '2':
            chart_data()
        elif choice == '3':
            train_model()
        elif choice == '4':
            analyze_model()
        elif choice == '5':
            print("\nExiting the application. Goodbye!")
            sys.exit(0)
        else:
            print("\nInvalid choice. Please enter a number between 1 and 5.")
            time.sleep(2)

if __name__ == "__main__":
    main()