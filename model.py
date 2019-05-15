from sf_scraper import mergeOVAToCleanedAll, scrapeTeamOVAAll
from current_form import add_current_details, add_current_details_all, get_current_season
from clean_data import clean_everything, combining_games, get_match_results_against, remove_goal_scores, copy_csv_file, \
    rmv_dir, save_new_data_to_database
from prediction import getCLF, prepare_data, predict_next_round
from current_fixtures import get_current_fixtures
from standings import get_standings, get_all_standings
import os
import datetime


def magic(should_train=True, data_year_available_from=1993, data_year_collect_from=2006):
    # Constants
    current_year = get_current_season()
    CURRENT_FILE = '{}-{}.csv'.format(current_year, current_year + 1)
    columns = ["Date", "HomeTeam", "AwayTeam", "FTHG", "FTAG", "FTR"]

    # Paths
    data_path = "Data"

    raw_data_path = os.path.join(data_path, 'raw_data')
    OVA_FILE_PATH = os.path.join(data_path, 'overall_team_rating')
    STANDINGS_PATH = os.path.join(data_path, 'standings')
    STATISTICS_PATH = os.path.join(data_path, 'statistics')
    RAW_CLEANED_DATA_FILE_PATH = os.path.join(data_path, 'raw_cleaned')
    CLEANED_DATA_FILE_PATH = os.path.join(data_path, 'cleaned')
    DATABASE_PATH = os.path.join(data_path, 'database.db')
    FINAL_FILE = os.path.join(data_path, 'final.csv')
    CLF_FILE = os.path.join(data_path, 'best_clf.joblib')
    CONFIDENCE_FILE = os.path.join(data_path, 'model_confidence1.csv')

    raw_data_path_current = os.path.join(raw_data_path, CURRENT_FILE)
    RAW_CLEANED_DATA_FILE_PATH_CURRENT = os.path.join(RAW_CLEANED_DATA_FILE_PATH, CURRENT_FILE)
    CLEANED_DATA_FILE_PATH_CURRENT = os.path.join(CLEANED_DATA_FILE_PATH, CURRENT_FILE)
    PRED_RANKING_ROUND_PATH = os.path.join(STATISTICS_PATH, 'round_rankings')
    PREDICTION_FILE = os.path.join(STATISTICS_PATH, 'prediction_result.csv')
    PRED_RANKING_FILE = os.path.join(STATISTICS_PATH, 'prediction_ranking.csv')
    PRED_RANKING_ROUND_SUMMARY_FILE = os.path.join(STATISTICS_PATH, 'round_rankings_summary.csv')
    CURRENT_STANDINGS_FILE = os.path.join(STANDINGS_PATH, CURRENT_FILE)

    # It is not necessary ti run these functions every time, however it is necessary uopn initial execution.
    # These functions do not have to be executed every time but recommended upon initial execution.

    # This is scraping the overall rating data from sofifa.
    # This takes quite a bit of time to run so I usually just run in once and then comment below.
    # SOFIFA updates their stat two or three times every month, but they don't change data much
    # scrapeTeamOVAAll(OVA_FILE_PATH, data_year_collect_from, current_year)

    # Pre-processing

    # 1.
    # Latest premier league results
    # This data can also be retrieved from http://www.football-data.co.uk/england.php
    # Uncomment below to get the latest match results
    # get_current_fixtures(raw_data_path_CURRENT)

    # 2. Standings (from 1993 to current year)
    # Uncomment below to run the function
    # getRankingsAll(data_year_available_from, current_year, RAW_CLEANED_DATA_FILE_PATH, STANDINGS_PATH)

    # Run the functions below to start generating necessary data

    # 1. From raw_data data, remove all data but the selected columns.
    # Produces: cleaned data csv located in CLEANED_DATA_FILE_PATH
    clean_everything(raw_data_path, RAW_CLEANED_DATA_FILE_PATH, columns, data_year_available_from, current_year)

    # 2. From 1, add Overall Rating columns
    # Produces: cleaned csv modified, located in CLEANED_DATA_FILE_PATH.
    # Now all cleaned csv from 2006-2018 have OVA column.
    mergeOVAToCleanedAll(OVA_FILE_PATH, RAW_CLEANED_DATA_FILE_PATH, data_year_collect_from, current_year)

    # 3. From 2, copy cleaned raw_data data to cleaned data for prediction purpose
    # Produces: copy csv from RAW_CLEANED_DATA_FILE_PATH to CLEANED_DATA_FILE_PATH
    copy_csv_file(RAW_CLEANED_DATA_FILE_PATH, CLEANED_DATA_FILE_PATH)

    # 4. From 3, add current status columns
    # (current point, current goal for,against,difference, match played, losing/winning streaks, last 5 games)
    # Produces: cleaned csv modified, located in CLEANED_DATA_FILE_PATH.
    # Now all cleaned csv from 1993-2018 have additional columns
    add_current_details_all(CLEANED_DATA_FILE_PATH, CLEANED_DATA_FILE_PATH, STANDINGS_PATH, data_year_available_from,
                            current_year, data_year_available_from)

    # 5. From 4, merge all csv files from startYear to endYear together.
    # FOR NOW, I only collect data from 2006 because sofifa only provides ova data from 2006,
    # and model tends to perform better with this approach
    # Produces: new csv file on FINAL_FILE
    combining_games(CLEANED_DATA_FILE_PATH, FINAL_FILE, data_year_collect_from, current_year)

    # 6. From 5, get all head-to-head results (match results against the other team over time)
    # Produces: edited final.csv file under data_path
    get_match_results_against(FINAL_FILE, CLEANED_DATA_FILE_PATH, data_path, data_year_available_from, current_year)

    # 7. Once all data is aggregated, we can now build a classifier that make predictions.
    # If 'recalculate' is set True, it runs multiple classifiers on this data,
    # and do some grid search on it if necessary, and finally generates 'model confidence.csv'
    # that records confidence score of each classifier.
    # If 'recalculate' is set False, and if clf_file exists, then it simply loads the clf from clf_file.
    # Produces: returns the best clf.
    best_clf, y_results = getCLF(FINAL_FILE, CONFIDENCE_FILE, CLF_FILE, recalculate=should_train)

    # 8. Now we make prediction.
    # This process is done by first predicting the upcoming round, then aggregate the result, then predict the next,
    # and repeat the process until there are no more games to predict. "predict_next_round"
    # also produces prediction probabilities
    # for each matches on stat_path.
    #  - 1. predict_next_round predicts next round and save the result in RAW_CLEANED_DATA_FILE_PATH_CURRENT.
    #  - 2. addCurrentDetails, as its name suggests, it adds current details.
    #  - 3. combineMatches combine all matches from 2006 to 2018
    #  - 4. getMatchResultsAgainst adds head-to-head results between two teams for each match
    is_first = True

    # First save current ranking before predicting results
    rmv_dir(STATISTICS_PATH)
    now = datetime.datetime.now().date().strftime('%Y-%m-%d')
    pred_ranking_round_file = os.path.join(PRED_RANKING_ROUND_PATH, 'prediction_ranking_{}.csv'.format(now))
    get_standings(RAW_CLEANED_DATA_FILE_PATH_CURRENT, pred_ranking_round_file, include_prediction=True,
                predicted_date_so_far=now, ranking_summary_file=PRED_RANKING_ROUND_SUMMARY_FILE)

    while True:
        isNextRound, date = predict_next_round(best_clf, FINAL_FILE, RAW_CLEANED_DATA_FILE_PATH_CURRENT,
                                               statistics=True, stat_path=PREDICTION_FILE, first=is_first)
        if not isNextRound:
            break
        add_current_details(RAW_CLEANED_DATA_FILE_PATH_CURRENT, CLEANED_DATA_FILE_PATH_CURRENT, STANDINGS_PATH,
                            data_year_available_from)
        combining_games(CLEANED_DATA_FILE_PATH, FINAL_FILE, data_year_collect_from, current_year)
        get_match_results_against(FINAL_FILE, CLEANED_DATA_FILE_PATH, data_path, data_year_available_from, current_year)
        pred_ranking_round_file = os.path.join(PRED_RANKING_ROUND_PATH, 'prediction_ranking_{}.csv'.format(date))
        get_standings(PREDICTION_FILE, pred_ranking_round_file, include_prediction=True, predicted_date_so_far=date,
                    ranking_summary_file=PRED_RANKING_ROUND_SUMMARY_FILE)
        is_first = False

    # 9. Now prediction is done. Produce a season standing with using the prediction result.
    get_standings(PREDICTION_FILE, PRED_RANKING_FILE, include_prediction=True)

    # 10. Put previous results, prediction results, standing predictions to the database
    save_new_data_to_database(DATABASE_PATH, FINAL_FILE, PREDICTION_FILE, PRED_RANKING_ROUND_SUMMARY_FILE)


if __name__ == "__main__":
    magic()
