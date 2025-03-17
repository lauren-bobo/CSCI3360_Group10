# Stock Market Prediction 
#Info 
Description: This repository contains a means to connecting 

## Setup
**requires** 
1.Kaggle username 
2. Kagglehub API Token (Settings> API:Create New Token, then locate the token number in your json file):

# Explanation: 
## Authentication
1. On first launch, the console will prompt Clone this repository
2. Install required packages:
   ```
   pip install kagglehub pandas seaborn tensorflow
   ```
   you may have to do several updates of kagglehub if its insatalled through pip. 


 Run <pyton run> in your console. This will automaticaally create {File ./config.json}, which 

## Usage: From Main working directory (Git clone/repository Main File)
1.     Run <./ pyton run> in your console. This will automaticaally create {File ./config.json}, an untracked file, which will enter these credentials in the future. (WORK IN PROGRESS: This will also be used to update the data each time the model is run if we don't struggle to train on). 

### Windows
Run the pipeline by typing:
```
python run
```
Into your dirrectory terminal. 
This will update and process the data automatically. 

## Authentication

On first run, you'll need to authenticate with Kaggle:

1. When prompted by the pipeline, enter your Kaggle username and API key (if you haven't set them in the `config.json` file). 
2. Your credentials will be saved for future use and untracked by the repository. 
after that, the dirrectory will save your credentials and automatically update the data on run. 