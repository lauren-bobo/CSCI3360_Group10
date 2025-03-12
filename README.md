# Stock Market Prediction 


## Setup

1. Clone this repository
2. Install required packages:
   ```
   pip install kagglehub pandas seaborn
   ```
   you may have to do several updates

#Info 
Due to torage limits and the need for API authentication, several files will not be shared on this repository,
including the data which is automatically obtained by the code and all compiled code/figs
See the .gitignore for untracked packages. 


## Obtaining Kaggle API Key

To run the pipeline, each user needs to obtain their own Kaggle API key:

1. Create a Kaggle account if you don't have one: [kaggle.com/account/login](https://www.kaggle.com/account/login)
2. Go to your Kaggle account settings: [kaggle.com/account](https://www.kaggle.com/account)
3. Scroll to the API section and click "Create New API Token"
4. This will download a file named `kaggle.json`. Move this file to the `~/.kaggle/` directory (create the directory if it doesn't exist).
5. Ensure the file has the correct permissions:
   ```
   chmod 600 ~/.kaggle/kaggle.json
   ```

## Usage

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