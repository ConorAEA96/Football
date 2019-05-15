from datetime import datetime as dt
import os
import pandas as pd
import ntpath
import numpy as np
import math
from distutils.dir_util import copy_tree
from shutil import rmtree
import sqlite3


# This function is used to make a directory.
def make_directory(path):
    directory = os.path.dirname(path)
    if not os.path.exists(directory):
        os.makedirs(directory)


# If a directory already exists it will be removed.
def rmv_dir(path):
    if os.path.exists(path):
        rmtree(path)


# This function is used to copy a file/folder.
def copy_csv_file(from_path_a, to_path_b):

    make_directory(to_path_b)

    if os.path.isfile(from_path_a):
        with open(to_path_b, 'w') as to_file, open(from_path_a, 'r') as from_file:

            for line in from_file:

                to_file.write(line)

    elif os.path.isdir(from_path_a):
        copy_tree(from_path_a, to_path_b)
    else:
        raise ValueError("There was an error while copying the csv file.")


'''The original data will be cleaned by removing the columns not needed and storing the ones that are.'''
# Parse data as time


def clean(from_path_a, to_path_b, cols):
    def convert_date(date):
        if date == '':
            return None
        else:
            _, file = ntpath.split(to_path_b)
            if len(date.split('-')) == 3:
                return date
            else:
                return dt.strptime(date, '%d/%m/%y').date()

    def convert_score(score):
        if math.isnan(score):
            return score
        else:
            return int(score)

    data_frame = pd.read_csv(from_path_a, error_bad_lines=False)
    data_frame = data_frame[cols]
    data_frame = data_frame[pd.notnull(data_frame['Date'])]

    data_frame['Date'] = data_frame['Date'].apply(convert_date)
    data_frame['FTHG'] = data_frame['FTHG'].apply(convert_score)
    data_frame['FTAG'] = data_frame['FTAG'].apply(convert_score)

    head, _ = ntpath.split(to_path_b)
    if not os.path.exists(head):
        os.makedirs(head)
    data_frame.to_csv(to_path_b, index=False)


# This function is cleaning the data in the raw_data folder from every year.
def clean_everything(from_folder_a, to_folder_b, cols, from_year_start, to_year_end):

    for years in range(from_year_start, to_year_end + 1):
        csv_file = '{}-{}.csv'.format(years, years + 1)

        from_path_1 = os.path.join(from_folder_a, csv_file)
        to_path_2 = os.path.join(to_folder_b, csv_file)

        print("Data cleaning", from_path_1, "...")
        clean(from_path_1, to_path_2, cols)


# The years are then concatenated through this function.
def combining_games(cleaned_folder_path, final_path, begin_year, end_year, make_file=True):

    print("Retrieving matches played from {} to {}...".format(begin_year, end_year))
    data_frame_list = []
    for year in range(begin_year, end_year + 1):
        file = '{}-{}.csv'.format(year, year + 1)
        path = os.path.join(cleaned_folder_path, file)
        data_frame = pd.read_csv(path)
        data_frame_list.append(data_frame)
    df = pd.concat(data_frame_list, ignore_index=True, sort=False)
    if make_file:
        df.to_csv(final_path, index=False)
    return df


def get_match_results_against(file_path, cleaned_folder_path, final_path, from_year, to_year):
    print("Getting head-to-head results...")
    team_detail, match_detail = {}, {}
    match_detail_columns = [
        'HT_win_rate_against',
        'AT_win_rate_against'
    ]

    for item in match_detail_columns:
        match_detail[item] = []

    # Getting the results from head-to-head matches from_year to_year
    df = combining_games(cleaned_folder_path, final_path, from_year, to_year, make_file=False)
    for index, row in df.iterrows():

        home_team = row['HomeTeam']
        away_team = row['AwayTeam']

        if home_team not in team_detail:
            team_detail[home_team] = {}

        if away_team not in team_detail:
            team_detail[away_team] = {}

        if away_team not in team_detail[home_team]:
            team_detail[home_team][away_team] = {
                'match_played': 0,
                'win': 0
            }
        if home_team not in team_detail[away_team]:
            team_detail[away_team][home_team] = {
                'match_played': 0,
                'win': 0
            }

        TD_HT_AT = team_detail[home_team][away_team]
        TD_AT_HT = team_detail[away_team][home_team]
        home_team_win_rate = TD_HT_AT['win'] / TD_HT_AT['match_played'] if TD_HT_AT['match_played'] > 0 else np.nan
        away_team_win_rate = TD_AT_HT['win'] / TD_AT_HT['match_played'] if TD_AT_HT['match_played'] > 0 else np.nan
        match_detail['HT_win_rate_against'].append(home_team_win_rate)
        match_detail['AT_win_rate_against'].append(away_team_win_rate)

        TD_HT_AT['match_played'] += 1
        TD_AT_HT['match_played'] += 1

        game_result = row['FTR']
        if game_result == 'H':
            TD_HT_AT['win'] += 1
        elif game_result == 'A':
            TD_AT_HT['win'] += 1

    # Only take the last x results of df and combine with filedf.
    # This is because we don't always want to merge all data from 1993 to 2018
    filed_f = pd.read_csv(file_path)
    row_count = filed_f.shape[0]
    filed_f['HT_win_rate_against'] = pd.Series(match_detail['HT_win_rate_against'][-row_count:], index=filed_f.index)
    filed_f['AT_win_rate_against'] = pd.Series(match_detail['AT_win_rate_against'][-row_count:], index=filed_f.index)
    filed_f.to_csv(file_path, index=False)


def remove_goal_scores(final_path):
    print("Removing Goal Scores...")
    df = pd.read_csv(final_path)
    df = df.drop(columns=['FTHG', 'FTAG'])
    df.to_csv(final_path, index=False)


def save_new_data_to_database(database_path, final_data_file, prediction_results_file, standing_predictions_file,
                              final_data_file_name='past_results',
                              prediction_results_file_name='results_prediction',
                              standing_predictions_file_name='table_standings_prediction'):
    conn = sqlite3.connect(database_path)

    previous_results_df = pd.read_csv(final_data_file)
    previous_results_df = previous_results_df[["Date", "HomeTeam", "AwayTeam", "FTHG", "FTAG", "FTR"]]
    previous_results_df = previous_results_df.loc[(previous_results_df['FTHG'] != 0) |
                                                  (previous_results_df['FTAG'] != 0) |
                                                  ((previous_results_df['FTR'] != 'A') &
                                                   (previous_results_df['FTR'] != 'H'))]

    prediction_results_df = pd.read_csv(prediction_results_file)
    prediction_results_df = prediction_results_df[["Date", "HomeTeam", "AwayTeam", "FTR", "prob_A", "prob_D", "prob_H"]]
    prediction_results_df = prediction_results_df.loc[prediction_results_df['prob_A'].notna()]

    standing_result_df = pd.read_csv(standing_predictions_file)

    previous_results_df.to_sql(final_data_file_name, con=conn, if_exists='replace')
    prediction_results_df.to_sql(prediction_results_file_name, con=conn, if_exists='replace')
    standing_result_df.to_sql(standing_predictions_file_name, con=conn, if_exists='replace')
