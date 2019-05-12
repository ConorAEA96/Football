from flask import Flask, render_template, request
import sqlite3
import json

app = Flask(__name__)
database_path = 'Data/database.db'


@app.route('/rankings')
def rankings():
    conn = sqlite3.connect(database_path)
    cur = conn.cursor()
    cur.execute('SELECT * FROM table_standings_prediction')
    rankings_raw = cur.fetchall()
    columns = [x[0] for x in cur.description]
    rankings = []
    for ranking in rankings_raw:
        ranking_on_date = {}
        for column, data in zip(columns[1:], ranking[1:]):
            ranking_on_date[column] = data
        rankings.append(ranking_on_date)

    return json.dumps(rankings)


@app.route('/predictions')
def predictions():
    conn = sqlite3.connect(database_path)
    cur = conn.cursor()

    query = 'SELECT * FROM results_prediction'
    req_params_raw = request.data
    if req_params_raw:
        req_params = json.loads(req_params_raw)
        query_type = 'AND' if 'against' in req_params else 'OR'
        teams = ["'" + team + "'" for team in req_params['teams']]
        teams = ",".join(teams)
        query += ' WHERE HomeTeam IN ({}) {} AwayTeam IN ({})'.format(teams, query_type, teams)

    cur.execute(query)
    predictions_raw = cur.fetchall()
    columns = [x[0] for x in cur.description]
    predictions = []
    for prediction in predictions_raw:
        prediction_match = {}
        for column, data in zip(columns[1:], prediction[1:]):
            prediction_match[column] = data
        predictions.append(prediction_match)

    return json.dumps(predictions)


@app.route('/past_results')
def past_results():
    conn = sqlite3.connect(database_path)
    cur = conn.cursor()

    query = 'SELECT * FROM past_results'
    req_params_raw = request.data
    if req_params_raw:
        req_params = json.loads(req_params_raw)
        query_type = 'AND' if 'against' in req_params else 'OR'
        teams = ["'" + team + "'" for team in req_params['teams']]
        teams = ",".join(teams)
        query += ' WHERE HomeTeam IN ({}) {} AwayTeam IN ({})'.format(teams, query_type, teams)

    cur.execute(query)
    previous_results_raw = cur.fetchall()
    columns = [x[0] for x in cur.description]
    past_results = []
    for result in previous_results_raw:
        match_result = {}
        for column, data in zip(columns[1:], result[1:]):
            match_result[column] = data
        past_results.append(match_result)

    return json.dumps(past_results)


if __name__ == '__main__':
        app.run()