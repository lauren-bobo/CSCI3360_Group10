# Stock Market Data Pipeline

A simple pipeline for downloading and processing stock market data from Kaggle.

## Setup

1. Clone this repository
2. Make the pipeline script executable:
   ```
   chmod +x run_pipeline.sh
   ```

## Usage

Run the pipeline with:

```
from pathlib import Path

# Get the project root directory
project_root = Path(__file__).parent.parent.parent
data_dir = project_root / "data" / "stock_data"

# Create directory if it doesn't exist
data_dir.mkdir(parents=True, exist_ok=True)

# Download the dataset
dataset_id = "nelgiriyewithana/world-stock-prices-daily-updating"
downloaded_path = kagglehub.dataset_download(
    dataset_id,
    path=str(data_dir),
    force_download=True
)