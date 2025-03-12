# Stock Market Data Pipeline

A simple pipeline for downloading and processing stock market data from Kaggle.

## Setup

1. Clone this repository
2. Install required packages:
   ```
   pip install kagglehub pandas
   ```

## Usage

### Windows
Run the pipeline with:
```
python src/data/pipeline.py
```

### Linux/Mac
Make the script executable and run:
```
chmod +x run_pipeline.sh
./run_pipeline.sh
```

## Authentication

On first run, you'll need to authenticate with Kaggle:

1. Create a Kaggle account if you don't have one: [kaggle.com/account/login](https://www.kaggle.com/account/login)
2. Go to your Kaggle account settings: [kaggle.com/account](https://www.kaggle.com/account)
3. Scroll to the API section and click "Create New API Token"
4. When prompted by the pipeline, enter your Kaggle username and API key

Your credentials will be saved for future use.