import pandas as pd
import numpy as np
import os
import datetime


'''If a team is on a particular streak it measures their current form.
If a team is on a win streak it is safe to assume that the likelihood of them winning 
their upcoming game is quite high.
Vice versa for teams that are on a losing streak.
 '''


def three_game_win_streak(previous_matches):
    if hasattr(previous_matches, "__len__"):
        return 1 if len(previous_matches) > 3 and previous_matches[-3:] == 'WWW' else 0
    return np.nan


def five_game_win_streak(previous_matches):
    if hasattr(previous_matches, "__len__"):
        return 1 if previous_matches == 'WWWWW' else 0
    return np.nan


def three_game_lose_streak(previous_matches):
    if hasattr(previous_matches, "__len__"):
        return 1 if len(previous_matches) > 3 and previous_matches[-3:] == 'LLL' else 0
    return np.nan


def five_game_lose_streak(previous_matches):
    if hasattr(previous_matches, "__len__"):
        return 1 if previous_matches == 'LLLLL' else 0
    return np.nan


def five_win_rate(previous_matches):
    if hasattr(previous_matches, "__len__") and len(previous_matches) == 5:
        win_count = previous_matches.count('W')
        return win_count / len(previous_matches)
    else:
        return np.nan


def get_current_season():
    current_date = datetime.datetime.now()
    start_of_new_season = datetime.datetime(current_date.year, 7, 1)
    return current_date.year if current_date > start_of_new_season else current_date.year - 1


#
# Calculate match played, current standing, goal for, goal against, goal difference, winning/losing streaks, etc.
# Input is csv that is just cleaned from raw_data data
# Output is csv modified with each row added match played, current standing, GF, GA, GD, winning/losing streaks, etc.
def add_current_details(from_path_a, to_path_b, standings_table_path, available_year):
    team_detail, match_detail = {}, {}
    match_detail_columns = [
        'home_team_current_standing',
        'home_team_match_played',
        'home_team_past_standing',
        'home_team_past_goal_diff',
        'home_team_past_win_rate',
        'home_team_goal_for',
        'home_team_goal_against',
        'home_team_goal_diff',
        'home_team_win_rate_season',
        'away_team_match_played',
        'away_team_current_standing',
        'away_team_past_standing',
        'away_team_past_goal_diff',
        'away_team_past_win_rate',
        'away_team_goal_for',
        'away_team_goal_against',
        'away_team_goal_diff',
        'away_team_win_rate_season',
        'home_team_last_5',
        'home_team_last_4',
        'home_team_last_3',
        'home_team_last_2',
        'home_team_last_1',
        'away_team_last_5',
        'away_team_last_4',
        'away_team_last_3',
        'away_team_last_2',
        'away_team_last_1'
    ]

    for item in match_detail_columns:
        match_detail[item] = []

    data_frame = pd.read_csv(from_path_a)

    previous_year = int(from_path_a[-13:-9]) - 1
    standings = dict()
    # We only have data from 1993 to current. That means We don't have 'previous year' data at 1993.
    if previous_year > available_year:
        df_standings = pd.read_csv('{}/{}-{}.csv'.format(standings_table_path, previous_year, previous_year + 1))
        for index, row in df_standings.iterrows():
            standings[row['Team']] = dict()
            standings[row['Team']]['Points'] = row['Points']
            standings[row['Team']]['Goal_Diff'] = row['Goal_Diff']
            standings[row['Team']]['Win_Rate'] = row['Win_Rate']

    for index, row in data_frame.iterrows():
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

        match_detail['home_team_match_played'].append(team_detail_home_team['match_played'])
        match_detail['home_team_current_standing'].append(team_detail_home_team['current_standing'])
        match_detail['home_team_past_standing'].append(team_detail_home_team['past_standing'])
        match_detail['home_team_past_goal_diff'].append(team_detail_home_team['past_goal_diff'])
        match_detail['home_team_past_win_rate'].append(team_detail_home_team['past_win_rate'])
        match_detail['home_team_goal_for'].append(team_detail_home_team['goal_for'])
        match_detail['home_team_goal_against'].append(team_detail_home_team['goal_against'])
        match_detail['home_team_goal_diff'].append(team_detail_home_team['goal_difference'])
        match_detail['away_team_match_played'].append(team_detail_away_team['match_played'])
        match_detail['away_team_current_standing'].append(team_detail_away_team['current_standing'])
        match_detail['away_team_past_standing'].append(team_detail_away_team['past_standing'])
        match_detail['away_team_past_goal_diff'].append(team_detail_away_team['past_goal_diff'])
        match_detail['away_team_past_win_rate'].append(team_detail_away_team['past_win_rate'])
        match_detail['away_team_goal_for'].append(team_detail_away_team['goal_for'])
        match_detail['away_team_goal_against'].append(team_detail_away_team['goal_against'])
        match_detail['away_team_goal_diff'].append(team_detail_away_team['goal_difference'])
        match_detail['home_team_win_rate_season'].append(
            team_detail_home_team['win'] / team_detail_home_team['match_played']
            if team_detail_home_team['match_played'] > 0 else np.nan)
        match_detail['away_team_win_rate_season'].append(
            team_detail_away_team['win'] / team_detail_away_team['match_played']
            if team_detail_away_team['match_played'] > 0 else np.nan)

        match_detail['home_team_last_5'].append(team_detail_home_team['last_5_matches'][0])
        match_detail['away_team_last_5'].append(team_detail_away_team['last_5_matches'][0])
        match_detail['home_team_last_4'].append(team_detail_home_team['last_5_matches'][1])
        match_detail['away_team_last_4'].append(team_detail_away_team['last_5_matches'][1])
        match_detail['home_team_last_3'].append(team_detail_home_team['last_5_matches'][2])
        match_detail['away_team_last_3'].append(team_detail_away_team['last_5_matches'][2])
        match_detail['home_team_last_2'].append(team_detail_home_team['last_5_matches'][3])
        match_detail['away_team_last_2'].append(team_detail_away_team['last_5_matches'][3])
        match_detail['home_team_last_1'].append(team_detail_home_team['last_5_matches'][4])
        match_detail['away_team_last_1'].append(team_detail_away_team['last_5_matches'][4])

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

    columnList = list(data_frame)

    for key, match_results in match_detail.items():
        data_frame[key] = pd.Series(match_results)
    df = data_frame[columnList + match_detail_columns]

    df['home_team_last_matches'] = df['home_team_last_5'] + df['home_team_last_4'] + df['home_team_last_3'] + df['home_team_last_2'] + df['home_team_last_1']
    df['away_team_last_matches'] = df['away_team_last_5'] + df['away_team_last_4'] + df['away_team_last_3'] + df['away_team_last_2'] + df['away_team_last_1']
    df['home_team_3_win_streak'] = df['home_team_last_matches'].apply(three_game_win_streak)
    df['home_team_5_win_streak'] = df['home_team_last_matches'].apply(five_game_win_streak)
    df['home_team_3_lose_Streak'] = df['home_team_last_matches'].apply(three_game_lose_streak)
    df['home_team_5_lose_Streak'] = df['home_team_last_matches'].apply(five_game_lose_streak)
    df['away_team_3_win_streak'] = df['away_team_last_matches'].apply(three_game_win_streak)
    df['away_team_5_win_streak'] = df['away_team_last_matches'].apply(five_game_win_streak)
    df['away_team_3_lose_Streak'] = df['away_team_last_matches'].apply(three_game_lose_streak)
    df['away_team_5_lose_Streak'] = df['away_team_last_matches'].apply(five_game_lose_streak)
    df['home_team_5_win_rate'] = df['home_team_last_matches'].apply(five_win_rate)
    df['away_team_5_win_rate'] = df['away_team_last_matches'].apply(five_win_rate)
    df['current_standing_diff'] = df['home_team_current_standing'] - df['away_team_current_standing']
    df['past_standing_diff'] = df['home_team_past_standing'] - df['away_team_past_standing']
    df['past_goal_diff_diff'] = df['home_team_past_goal_diff'] - df['away_team_past_goal_diff']
    df['past_win_rate_diff'] = df['home_team_past_win_rate'] - df['away_team_past_win_rate']
    df['past_standing_diff'] = df['home_team_past_standing'] - df['away_team_past_standing']
    df['win_rate_season_diff'] = df['home_team_win_rate_season'] - df['away_team_win_rate_season']
    df['goal_diff_diff'] = df['home_team_goal_diff'] - df['away_team_goal_diff']

    dropLabels = ['home_team_last_' + str(x + 1) for x in range(5)] + ['away_team_last_' + str(x + 1) for x in range(5)]
    dropLabels += ['home_team_last_matches', 'away_team_last_matches']
    df = df.drop(columns=dropLabels)

    df.to_csv(to_path_b, index=False)


def add_current_details_all(from_folder_path, to_folder_path, standings_path, from_year, to_year, year_available_from):
    for year in range(from_year, to_year + 1):
        file = '{}-{}.csv'.format(year, year + 1)
        from_path = os.path.join(from_folder_path, file)
        to_path = os.path.join(to_folder_path, file)
        print("About to add 'current details' from {} to {}...".format(from_path, to_path))
        add_current_details(from_path, to_path, standings_path, year_available_from)
