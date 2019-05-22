import pandas as pd
import numpy as np
import os
import datetime


# Helpers
# Identify Win/Loss Streaks if any.
def get_3game_ws(last_matches):
    if hasattr(last_matches, "__len__"):
        return 1 if len(last_matches) > 3 and last_matches[-3:] == 'WWW' else 0
    return np.nan


def get_5game_ws(last_matches):
    if hasattr(last_matches, "__len__"):
        return 1 if last_matches == 'WWWWW' else 0
    return np.nan


def get_3game_ls(last_matches):
    if hasattr(last_matches, "__len__"):
        return 1 if len(last_matches) > 3 and last_matches[-3:] == 'LLL' else 0
    return np.nan


def get_5game_ls(last_matches):
    if hasattr(last_matches, "__len__"):
        return 1 if last_matches == 'LLLLL' else 0
    return np.nan


def get_5win_rate(last_matches):
    if hasattr(last_matches, "__len__") and len(last_matches) == 5:
        win_count = last_matches.count('W')
        return win_count / len(last_matches)
    else:
        return np.nan


def get_current_season():
    now = datetime.datetime.now()
    # By July, fixture of the season should be available.
    new_season_start = datetime.datetime(now.year, 7, 1)
    return now.year if now > new_season_start else now.year - 1


# Calculate match played, current standing, goal for, goal against, goal difference, winning/losing streaks, etc.
# Input is csv that is just cleaned from raw_data data
# Output is csv modified with each row added match played, current standing, GF, GA, GD, winning/losing streaks, etc.
def add_current_details(from_path, to_path, standings_path, year_available_from):
    team_detail, match_detail = {}, {}
    match_detail_columns = [
        'HT_match_played',
        'HT_current_standing',
        'HT_past_standing',
        'HT_past_goal_diff',
        'HT_past_win_rate',
        'HT_goal_for',
        'HT_goal_against',
        'HT_goal_diff',
        'HT_win_rate_season',
        'AT_match_played',
        'AT_current_standing',
        'AT_past_standing',
        'AT_past_goal_diff',
        'AT_past_win_rate',
        'AT_goal_for',
        'AT_goal_against',
        'AT_goal_diff',
        'AT_win_rate_season',
        'HT_last_5',
        'HT_last_4',
        'HT_last_3',
        'HT_last_2',
        'HT_last_1',
        'AT_last_5',
        'AT_last_4',
        'AT_last_3',
        'AT_last_2',
        'AT_last_1'
    ]

    for item in match_detail_columns:
        match_detail[item] = []

    df = pd.read_csv(from_path)

    previous_year = int(from_path[-13:-9]) - 1
    standings = dict()
    # We only have data from 1993 to current. That means We don't have 'previous year' data at 1993.
    if previous_year > year_available_from:
        df_standings = pd.read_csv('{}/{}-{}.csv'.format(standings_path, previous_year, previous_year + 1))
        for index, row in df_standings.iterrows():
            standings[row['Team']] = dict()
            standings[row['Team']]['Points'] = row['Points']
            standings[row['Team']]['Goal_Diff'] = row['Goal_Diff']
            standings[row['Team']]['Win_Rate'] = row['Win_Rate']

    for index, row in df.iterrows():
        home_team = row['HomeTeam']
        away_team = row['AwayTeam']

        if home_team not in team_detail:
            team_detail[home_team] = {
                'match_played': 0,
                'win': 0,
                'current_standing': 0,
                'past_standing': standings[home_team]['Points'] if home_team in standings else -1,
                'past_goal_diff': standings[home_team]['Goal_Diff'] if home_team in standings else -1,
                'past_win_rate': standings[home_team]['Win_Rate'] if home_team in standings else 0,
                'goal_for': 0,
                'goal_against': 0,
                'goal_difference': 0,
                'last_5_matches': [""] * 5
            }
        if away_team not in team_detail:
            team_detail[away_team] = {
                'match_played': 0,
                'win': 0,
                'current_standing': 0,
                'past_standing': standings[away_team]['Points'] if away_team in standings else -1,
                'past_goal_diff': standings[away_team]['Goal_Diff'] if away_team in standings else -1,
                'past_win_rate': standings[away_team]['Win_Rate'] if away_team in standings else 0,
                'goal_for': 0,
                'goal_against': 0,
                'goal_difference': 0,
                'last_5_matches': [""] * 5
            }

        team_detail_home_team = team_detail[home_team]
        team_detail_away_team = team_detail[away_team]

        if len(team_detail_home_team['last_5_matches']) != 5 or len(team_detail_away_team['last_5_matches']) != 5:
            break

        match_detail['HT_match_played'].append(team_detail_home_team['match_played'])
        match_detail['HT_current_standing'].append(team_detail_home_team['current_standing'])
        match_detail['HT_past_standing'].append(team_detail_home_team['past_standing'])
        match_detail['HT_past_goal_diff'].append(team_detail_home_team['past_goal_diff'])
        match_detail['HT_past_win_rate'].append(team_detail_home_team['past_win_rate'])
        match_detail['HT_goal_for'].append(team_detail_home_team['goal_for'])
        match_detail['HT_goal_against'].append(team_detail_home_team['goal_against'])
        match_detail['HT_goal_diff'].append(team_detail_home_team['goal_difference'])
        match_detail['AT_match_played'].append(team_detail_away_team['match_played'])
        match_detail['AT_current_standing'].append(team_detail_away_team['current_standing'])
        match_detail['AT_past_standing'].append(team_detail_away_team['past_standing'])
        match_detail['AT_past_goal_diff'].append(team_detail_away_team['past_goal_diff'])
        match_detail['AT_past_win_rate'].append(team_detail_away_team['past_win_rate'])
        match_detail['AT_goal_for'].append(team_detail_away_team['goal_for'])
        match_detail['AT_goal_against'].append(team_detail_away_team['goal_against'])
        match_detail['AT_goal_diff'].append(team_detail_away_team['goal_difference'])
        match_detail['HT_win_rate_season'].append(
            team_detail_home_team['win'] / team_detail_home_team['match_played']
            if team_detail_home_team['match_played'] > 0 else np.nan)
        match_detail['AT_win_rate_season'].append(
            team_detail_away_team['win'] / team_detail_away_team['match_played']
            if team_detail_away_team['match_played'] > 0 else np.nan)

        match_detail['HT_last_5'].append(team_detail_home_team['last_5_matches'][0])
        match_detail['AT_last_5'].append(team_detail_away_team['last_5_matches'][0])
        match_detail['HT_last_4'].append(team_detail_home_team['last_5_matches'][1])
        match_detail['AT_last_4'].append(team_detail_away_team['last_5_matches'][1])
        match_detail['HT_last_3'].append(team_detail_home_team['last_5_matches'][2])
        match_detail['AT_last_3'].append(team_detail_away_team['last_5_matches'][2])
        match_detail['HT_last_2'].append(team_detail_home_team['last_5_matches'][3])
        match_detail['AT_last_2'].append(team_detail_away_team['last_5_matches'][3])
        match_detail['HT_last_1'].append(team_detail_home_team['last_5_matches'][4])
        match_detail['AT_last_1'].append(team_detail_away_team['last_5_matches'][4])

        team_detail_home_team['match_played'] += 1
        team_detail_away_team['match_played'] += 1
        team_detail_home_team['goal_for'] += row['FTHG']
        team_detail_away_team['goal_for'] += row['FTAG']
        team_detail_home_team['goal_against'] += row['FTAG']
        team_detail_away_team['goal_against'] += row['FTHG']

        gd = row['FTHG'] - row['FTAG']
        team_detail_home_team['goal_difference'] += gd
        team_detail_away_team['goal_difference'] -= gd

        team_detail_home_team['last_5_matches'].pop(0)
        team_detail_away_team['last_5_matches'].pop(0)

        game_result = row['FTR']
        if game_result == 'H':
            team_detail_home_team['current_standing'] += 3
            team_detail_home_team['win'] += 1
            team_detail_home_team['last_5_matches'].append('W')
            team_detail_away_team['last_5_matches'].append('L')
        elif game_result == 'A':
            team_detail_away_team['current_standing'] += 3
            team_detail_away_team['win'] += 1
            team_detail_home_team['last_5_matches'].append('L')
            team_detail_away_team['last_5_matches'].append('W')
        elif game_result == 'D':
            team_detail_home_team['current_standing'] += 1
            team_detail_away_team['current_standing'] += 1
            team_detail_home_team['last_5_matches'].append('D')
            team_detail_away_team['last_5_matches'].append('D')

    columnList = list(df)

    for key, match_results in match_detail.items():
        df[key] = pd.Series(match_results)
    df = df[columnList + match_detail_columns]

    df['HT_last_matches'] = df['HT_last_5'] + df['HT_last_4'] + df['HT_last_3'] + df['HT_last_2'] + df['HT_last_1']
    df['AT_last_matches'] = df['AT_last_5'] + df['AT_last_4'] + df['AT_last_3'] + df['AT_last_2'] + df['AT_last_1']
    df['HT_3_win_streak'] = df['HT_last_matches'].apply(get_3game_ws)
    df['HT_5_win_streak'] = df['HT_last_matches'].apply(get_5game_ws)
    df['HT_3_lose_Streak'] = df['HT_last_matches'].apply(get_3game_ls)
    df['HT_5_lose_Streak'] = df['HT_last_matches'].apply(get_5game_ls)
    df['AT_3_win_streak'] = df['AT_last_matches'].apply(get_3game_ws)
    df['AT_5_win_streak'] = df['AT_last_matches'].apply(get_5game_ws)
    df['AT_3_lose_Streak'] = df['AT_last_matches'].apply(get_3game_ls)
    df['AT_5_lose_Streak'] = df['AT_last_matches'].apply(get_5game_ls)
    df['HT_5_win_rate'] = df['HT_last_matches'].apply(get_5win_rate)
    df['AT_5_win_rate'] = df['AT_last_matches'].apply(get_5win_rate)
    df['current_standing_diff'] = df['HT_current_standing'] - df['AT_current_standing']
    df['past_standing_diff'] = df['HT_past_standing'] - df['AT_past_standing']
    df['past_goal_diff_diff'] = df['HT_past_goal_diff'] - df['AT_past_goal_diff']
    df['past_win_rate_diff'] = df['HT_past_win_rate'] - df['AT_past_win_rate']
    df['past_standing_diff'] = df['HT_past_standing'] - df['AT_past_standing']
    df['win_rate_season_diff'] = df['HT_win_rate_season'] - df['AT_win_rate_season']
    df['goal_diff_diff'] = df['HT_goal_diff'] - df['AT_goal_diff']

    dropLabels = ['HT_last_' + str(x + 1) for x in range(5)] + ['AT_last_' + str(x + 1) for x in range(5)]
    dropLabels += ['HT_last_matches', 'AT_last_matches']
    df = df.drop(columns=dropLabels)

    df.to_csv(to_path, index=False)


def add_current_details_all(from_folder_path, to_folder_path, standings_path, from_year, to_year, year_available_from):
    for year in range(from_year, to_year + 1):
        file = '{}-{}.csv'.format(year, year + 1)
        from_path = os.path.join(from_folder_path, file)
        to_path = os.path.join(to_folder_path, file)
        print("About to add 'current details' from {} to {}...".format(from_path, to_path))
        add_current_details(from_path, to_path, standings_path, year_available_from)