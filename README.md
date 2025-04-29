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
   pip install -r requirements.tx
   ```
  

#Info 
Due to storage limits and the need for API authentication, several files will not be shared on this repository,
including the data which is automatically obtained by the code and all compiled code/figs
See the .gitignore for untracked packages. 


## Obtaining Kaggle API Key

To run the pipeline, each user needs to obtain their own Kaggle API key:

1. Create a Kaggle account if you don't have one: [kaggle.com/account/login](https://www.kaggle.com/account/login)
2. Go to your Kaggle account settings: [kaggle.com/account](https://www.kaggle.com/account)
3. Scroll to the API section and click "Create New API Token"
4. This will download a file named `kaggle.json`. open this file for your API token
5. run run.py and enter your username and token when prompted. this will automatically configure the api :) see authentication.  
   

## Usage

### Windows
Run the pipeline by typing:
```
python run
```
Into your dirrectory terminal. 
This will update and process the data automatically. 

## Authentication
#the code is contained in pipeline.py
On first run, you'll need to authenticate with Kaggle:

1. When prompted by the pipeline, enter your Kaggle username and API key (if you haven't set them in the `config.json` file). 
2. Your credentials will be saved for future use and untracked by the repository. 
after that, the dirrectory will save your credentials and automatically update the data on run.
## Run 
run will authenticate with the kaggle API, run the data analysis, preprocess the data, and train the model. eventually, this will run on a switch statement to allow for chosing to retrieve data, generate analysis figs, train model, and test model from the console. 
## Data 
pipeline : handles the API retrieval/authentication and will house data preprocessing funtions. running this file will automatically retireve the data and preprocess it into a dataframe. 
# To Do : implement date time with O/S to update once per day only 

analysis: contains functions that create charts of the data for analysis and preprocessing. 

## model 
trainLSTM: purely implemented to process data into correct format for LSTM. 
