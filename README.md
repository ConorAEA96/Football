# English-Premier-League-Prediction
Applying Machine Learning Techniques to Predict the Outcome of Football Matches


[Demo App](https://conor-prem-league-predictor.herokuapp.com/)


&nbsp;
&nbsp;


## To Run
> python3 model.py

***Warning***: Few python packages required to run the script. Install them all, or use a 3rd party IDE (such as spyder) that pre-installs these packages by default.


&nbsp;
&nbsp;

## Scripts
#### 1. clean_data.py
- Includes necessary helper functions to process raw data
#### 2. current_fixtures
- Collects and adds more details to the processed raw data
- current/past standings, goals for/against/differences, etc.
#### 3. current_form
- Collects the latest match results
#### 4. standings.py
- Calculate league points and generate standings
#### 5. sf_scraper.py
- Scrape overall team stat from FIFA
#### 6. prediction.py
- With using processed data, train a ML model to predict future results
#### 7. model.py
- I/O file where the functions from the above files are actually executed

&nbsp;
&nbsp;



## Data
#### 1. Data/overall_team_rating(directory)
- scraped overall team stat data
#### 2. Data/standings (directory)
- historical standing results calculated in rankings.py
#### 3. Data/raw_data (directory)
- manually collected historical data of match outcomes
- latest match outcomes of the current season
#### 4. Data/raw_cleaned (directory)
- data extracted from data/raw
#### 5. Data/cleaned (directory)
- data processed from data/raw_cleaned
#### 6. Data/statistics (directory)
1. data/statistics/round_rankings (directory)
	- standings calculated based on the predicted match outcomes
	- each file in the directory has a date included in its name. It provides predicted standing outcomes at the denoted date
2. data/statistics/prediction_ranking.csv
	- predicted standing at the end of the season
3. data/statistics/prediction_result.csv
	- individual predicted match outcomes
4. data/statistics/round_rankings_summary.csv
	- predicted standing summary over the course of the season
#### 7. Data/best_clf.joblib
- disk cache of classifier that gives the best accuracy of prediction
#### 8. Data/database.db
- sql database that stores previous match outcomes, predicted match results and predicted standings
#### 9. Data/final.csv
- csv file used for training a model and making predictions
#### 10. Data/model_confidence1.csv
- list of grid searched classifiers and its confidence score



