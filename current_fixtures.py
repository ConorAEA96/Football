import pandas as pd
import requests
import numpy as np


'''The following teams below are the teams included in this current season of the English Premier League.'''


def team_name_conversion(teams):
    team_name_map = {
        'Arsenal FC': 'Arsenal',
        'AFC Bournemouth': 'Bournemouth',
        'Brighton & Hove Albion FC': 'Brighton',
        'Burnley FC': 'Burnley',
        'Cardiff City FC': 'Cardiff',
        'Chelsea FC': 'Chelsea',
        'Crystal Palace FC': 'Crystal Palace',
        'Everton FC': 'Everton',
        'Fulham FC': 'Fulham',
        'Huddersfield Town AFC': 'Huddersfield',
        'Leicester City FC': 'Leicester',
        'Liverpool FC': 'Liverpool',
        'Manchester City FC': 'Man City',
        'Manchester United FC': 'Man United',
        'Newcastle United FC': 'Newcastle',
        'Southampton FC': 'Southampton',
        'Tottenham Hotspur FC': 'Tottenham',
        'Watford FC': 'Watford',
        'West Ham United FC': 'West Ham',
        'Wolverhampton Wanderers FC': 'Wolves',
    }

    return team_name_map[teams]


def get_current_fixtures(raw_data_current_path):
    url = "http://api.football-data.org/v2/competitions/"
    authentication = "524232deb6634c2badc78820af20de35"
    headers = {"X-Auth-Token": authentication}

    print("Retrieving fixtures and results for the year...")

    england_area_code = 2072
    competition_url = url + "?areas=" + str(england_area_code)
    request = requests.get(competition_url, headers=headers).json()

    premier_league_data = [x for x in request['competitions'] if x['name'] == 'Premier League'][0]
    premier_league_id = premier_league_data['id']

    matches_url = url + str(premier_league_id) + "/matches"
    match_data = requests.get(matches_url, headers=headers).json()['matches']

    matches_dict = {
        'Date': [match['utcDate'].split('T')[0] for match in match_data],
        'HomeTeam': [team_name_conversion(match['homeTeam']['name']) for match in match_data],
        'AwayTeam': [team_name_conversion(match['awayTeam']['name']) for match in match_data],
        'FTHG': [match['score']['fullTime']['homeTeam'] if match['status'] == "FINISHED" else np.nan for match in
                 match_data],
        'FTAG': [match['score']['fullTime']['awayTeam'] if match['status'] == "FINISHED" else np.nan for match in
                 match_data],
        'FTR': [match['score']['winner'][0] if match['status'] == "FINISHED" and match['score']['winner'] else "" for
                match in match_data]
    }

    df = pd.DataFrame(matches_dict)
    df.to_csv(raw_data_current_path, index=False)

