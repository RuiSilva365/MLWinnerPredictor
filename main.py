import base64
import csv

import pandas as pd
from flask import Flask, render_template, request, flash, jsonify, session
import treatment
import url

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Necessário para usar flash messages
app.static_folder = 'static'

def handler_team(season, star_league, star_club):
    pd.set_option('display.max_columns', None)
    columns_remove = ['PSD', 'PSA']
    dfs = []  # List to hold DataFrames
    if star_league in url.file_path_leagues:
        csvs_path = url.file_path_builder(star_league, season, 2324)
        for path in csvs_path:
            df = treatment.cut_useless_rows(path)
            df = treatment.filter_club_games(star_club, df)
            dfs.append(df)  # Append each DataFrame to the list
        df_concatenated = pd.concat(dfs)  # Concatenate all DataFrames
        df.drop(columns=df.columns[1:], inplace=True)
        df_concatenated.to_csv("TeamGames.csv")
        return df
    else:
        return None

def handler_opp(season, star_league, opp_club):
    pd.set_option('display.max_columns', None)
    columns_remove = ['PSD', 'PSA']
    dfs = []  # List to hold DataFrames
    if star_league in url.file_path_leagues:
        csvs_path = url.file_path_builder(star_league, season, 2324)
        for path in csvs_path:
            df = treatment.cut_useless_rows(path)
            df = treatment.filter_club_games(opp_club, df)
            dfs.append(df)  # Append each DataFrame to the list
        df_concatenated = pd.concat(dfs)  # Concatenate all DataFrames
        df.drop(columns=df.columns[1:], inplace=True)
        df_concatenated.to_csv("OppGames.csv")
        return df
    else:
        return None

@app.route('/')
def index():
    if 'odds_data' in session:
        odds_data = session['odds_data']
        # Renderiza o template 'index.html' com os dados disponíveis
        return render_template('index.html', odds_data=odds_data)
    else:
        # Se não houver dados disponíveis, renderiza apenas o template 'index.html'
        return render_template('index.html')


@app.route('/update_data', methods=['POST'])
def update_data():
    data = request.json
    selected_season = data.get('season')
    star_league = data.get('league')
    star_club = data.get('club1')
    opp_club = data.get('club2')

    if not all([selected_season, star_league, star_club, opp_club]):
        return jsonify({"error": "Parâmetros ausentes."}), 400

    team_df = handler_team(selected_season, star_league, star_club)
    opp_df = handler_opp(selected_season, star_league, opp_club)

    if team_df is not None and opp_df is not None:
        return jsonify({"success": "Dados atualizados com sucesso."}), 200
    else:
        return jsonify({"error": "Arquivos CSV não encontrados."}), 404

def fetch_odds_from_url(url):
    try:
        score_odds = treatment.getNextgameData(url)
        url = treatment.transform_url(url)
        goals_odds = treatment.getNextgameGoalsData(url)
        score_odds.update(goals_odds)

        # Convertendo os dados para uma lista e mantendo a ordem dos valores
        odds_list = [score_odds[key] for key in ['B365H', 'B365D', 'B365A', 'BWH', 'BWD', 'BWA',
                                                 'MaxH', 'MaxD', 'MaxA', 'AvgH', 'AvgD', 'AvgA']]

        return odds_list
    except Exception as e:
        # Se ocorrer algum erro, vamos imprimir o erro para entender o que está acontecendo
        print("Error fetching odds:", e)
        # E retornar um erro JSON para o cliente
        return {"error": str(e)}

@app.route('/fetch_odds', methods=['POST'])
def fetch_odds():
    data = request.json
    url = data.get('url')
    if not url:
        return jsonify({"error": "URL não fornecida."}), 400

    try:
        odds_data = fetch_odds_from_url(url)
        session['odds_data'] = odds_data
        return jsonify({"odds": odds_data})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/save_validation_data', methods=['POST'])
def save_validation_data():
    data = request.json

    fields = ['B365H', 'B365D', 'B365A', 'BWH', 'BWD', 'BWA', 'MaxH', 'MaxD', 'MaxA', 'AvgH', 'AvgD', 'AvgA']
    filename = 'NextGame.csv'

    try:
        with open(filename, 'a', newline='') as csvfile:  # Abra o arquivo em modo de anexar
            writer = csv.DictWriter(csvfile, fieldnames=fields)
            if csvfile.tell() == 0:  # Verifique se o arquivo está vazio para escrever o cabeçalho
                writer.writeheader()
            writer.writerow(data)

        return jsonify({"success": "Dados salvos com sucesso."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
