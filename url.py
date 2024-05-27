#LISTA DE LIGAS
available_leagues = ["Premier League", "Bundesliga", "La Liga", "Serie A", "Primeira Liga", "Ligue 1"]

clubs_by_league = {
    "Premier League": [
        "Burnley", "Arsenal", "Bournemouth", "Brighton", "Everton",
        "Sheffield United", "Newcastle", "Brentford", "Chelsea", "Man United",
        "Nott'm Forest", "Fulham", "Liverpool", "Wolves", "Tottenham",
        "Man City", "Aston Villa", "West Ham", "Crystal Palace", "Luton"
    ],
    "Bundesliga": [
        "Werder Bremen", "Augsburg", "Hoffenheim", "Leverkusen", "Stuttgart",
        "Wolfsburg", "Dortmund", "Union Berlin", "Ein Frankfurt", "RB Leipzig",
        "Bochum", "Darmstadt", "FC Koln", "Freiburg", "Heidenheim", "M'gladbach",
        "Mainz", "Bayern Munich"
    ],
    "La Liga": [
        "Almeria", "Sevilla", "Sociedad", "Las Palmas", "Ath Bilbao",
        "Celta", "Villarreal", "Getafe", "Cadiz", "Ath Madrid",
        "Mallorca", "Valencia", "Osasuna", "Girona", "Barcelona",
        "Betis", "Alaves", "Granada", "Vallecano", "Real Madrid"
    ],
    "Serie A": [
        "Empoli", "Frosinone", "Genoa", "Inter", "Roma",
        "Sassuolo", "Lecce", "Udinese", "Torino", "Bologna",
        "Monza", "Milan", "Verona", "Fiorentina", "Juventus",
        "Lazio", "Napoli", "Salernitana", "Cagliari", "Atalanta"
    ],
    "Primeira Liga": [
        "Sp Braga", "Porto", "Benfica", "Sp Lisbon", "Guimaraes",
        "Pacos de Ferreira", "Boavista", "Famalicao", "Portimonense", "Vizela",
        "Farense", "Chaves", "Gil Vicente", "Estrela", "Arouca", "Casa Pia"
    ],
    "Ligue 1": [
        "Nice", "Lille", "Marseille", "PSG", "Brest", "Montpellier", "Nantes",
        "Rennes", "Strasbourg", "Metz", "Lyon", "Lorient", "Monaco", "Clermont",
        "Le Havre", "Reims", "Toulouse", "Lens"
    ]
}


# Dicionário com os URLs das ligas
file_path_leagues = {
    "Premier League": "https://www.football-data.co.uk/englandm.php",
    "Bundesliga": "https://www.football-data.co.uk/germanym.php",
    "La Liga": "https://www.football-data.co.uk/spainm.php",
    "Serie A": "https://www.football-data.co.uk/italym.php",
    "Primeira Liga": "https://www.football-data.co.uk/portugalm.php",
    "Ligue 1": "https://www.football-data.co.uk/francem.php"
    # Adicione outras ligas conforme necessário
}


#ENGLISH LEAGUE - PREMIER LEAGUE
file_path_premierleague = {
    "premierleague_1516": "https://www.football-data.co.uk/mmz4281/1516/E0.csv",
    "premierleague_1617": "https://www.football-data.co.uk/mmz4281/1617/E0.csv",
    "premierleague_1718": "https://www.football-data.co.uk/mmz4281/1718/E0.csv",
    "premierleague_1819": "https://www.football-data.co.uk/mmz4281/1819/E0.csv",
    "premierleague_1920": "https://www.football-data.co.uk/mmz4281/1920/E0.csv",
    "premierleague_2021": "https://www.football-data.co.uk/mmz4281/2021/E0.csv",
    "premierleague_2122": "https://www.football-data.co.uk/mmz4281/2122/E0.csv",
    "premierleague_2223": "https://www.football-data.co.uk/mmz4281/2223/E0.csv",
    "premierleague_2324": "https://www.football-data.co.uk/mmz4281/2324/E0.csv"
}

#GERMAN LEAGUE
file_path_bundesliga = {
    "bundesliga_1516": "https://www.football-data.co.uk/mmz4281/1516/D1.csv",
    "bundesliga_1617": "https://www.football-data.co.uk/mmz4281/1617/D1.csv",
    "bundesliga_1718": "https://www.football-data.co.uk/mmz4281/1718/D1.csv",
    "bundesliga_1819": "https://www.football-data.co.uk/mmz4281/1819/D1.csv",
    "bundesliga_1920": "https://www.football-data.co.uk/mmz4281/1920/D1.csv",
    "bundesliga_2021": "https://www.football-data.co.uk/mmz4281/2021/D1.csv",
    "bundesliga_2122": "https://www.football-data.co.uk/mmz4281/2122/D1.csv",
    "bundesliga_2223": "https://www.football-data.co.uk/mmz4281/2223/D1.csv",
    "bundesliga_2324": "https://www.football-data.co.uk/mmz4281/2324/D1.csv"
}



#PORTUGUESE LEAGUE- PRIMEIRA LIGA
file_path_primeiraliga = {
    "portugueseleague_1516": "https://www.football-data.co.uk/mmz4281/1516/P1.csv",
    "portugueseleague_1617": "https://www.football-data.co.uk/mmz4281/1617/P1.csv",
    "portugueseleague_1718": "https://www.football-data.co.uk/mmz4281/1718/P1.csv",
    "portugueseleague_1819": "https://www.football-data.co.uk/mmz4281/1819/P1.csv",
    "portugueseleague_1920": "https://www.football-data.co.uk/mmz4281/1920/P1.csv",
    "portugueseleague_2021": "https://www.football-data.co.uk/mmz4281/2021/P1.csv",
    "portugueseleague_2122": "https://www.football-data.co.uk/mmz4281/2122/P1.csv",
    "portugueseleague_2223": "https://www.football-data.co.uk/mmz4281/2223/P1.csv",
    "portugueseleague_2324": "https://www.football-data.co.uk/mmz4281/2324/P1.csv"
}

#SPANISH LEAGUE- LA LIGA
file_path_laliga = {
    "laliga_1516": "https://www.football-data.co.uk/mmz4281/1516/SP1.csv",
    "laliga_1617": "https://www.football-data.co.uk/mmz4281/1617/SP1.csv",
    "laliga_1718": "https://www.football-data.co.uk/mmz4281/1718/SP1.csv",
    "laliga_1819": "https://www.football-data.co.uk/mmz4281/1819/SP1.csv",
    "laliga_1920": "https://www.football-data.co.uk/mmz4281/1920/SP1.csv",
    "laliga_2021": "https://www.football-data.co.uk/mmz4281/2021/SP1.csv",
    "laliga_2122": "https://www.football-data.co.uk/mmz4281/2122/SP1.csv",
    "laliga_2223": "https://www.football-data.co.uk/mmz4281/2223/SP1.csv",
    "laliga_2324": "https://www.football-data.co.uk/mmz4281/2324/SP1.csv"
}

file_path_seriea = {
    "seriea_1516": "https://www.football-data.co.uk/mmz4281/1516/I1.csv",
    "seriea_1617": "https://www.football-data.co.uk/mmz4281/1617/I1.csv",
    "seriea_1718": "https://www.football-data.co.uk/mmz4281/1718/I1.csv",
    "seriea_1819": "https://www.football-data.co.uk/mmz4281/1819/I1.csv",
    "seriea_1920": "https://www.football-data.co.uk/mmz4281/1920/I1.csv",
    "seriea_2021": "https://www.football-data.co.uk/mmz4281/2021/I1.csv",
    "seriea_2122": "https://www.football-data.co.uk/mmz4281/2122/I1.csv",
    "seriea_2223": "https://www.football-data.co.uk/mmz4281/2223/I1.csv",
    "seriea_2324": "https://www.football-data.co.uk/mmz4281/2324/I1.csv"
}

file_path_ligue1 = {
    "ligue1_1516": "https://www.football-data.co.uk/mmz4281/1516/F1.csv",
    "ligue1_1617": "https://www.football-data.co.uk/mmz4281/1617/F1.csv",
    "ligue1_1718": "https://www.football-data.co.uk/mmz4281/1718/F1.csv",
    "ligue1_1819": "https://www.football-data.co.uk/mmz4281/1819/F1.csv",
    "ligue1_1920": "https://www.football-data.co.uk/mmz4281/1920/F1.csv",
    "ligue1_2021": "https://www.football-data.co.uk/mmz4281/2021/F1.csv",
    "ligue1_2122": "https://www.football-data.co.uk/mmz4281/2122/F1.csv",
    "ligue1_2223": "https://www.football-data.co.uk/mmz4281/2223/F1.csv",
    "ligue1_2324": "https://www.football-data.co.uk/mmz4281/2324/F1.csv"
}

# Obter o URL específico do arquivo CSV para a liga selecionada
league_file_paths = {
    "Premier League": file_path_premierleague,
    "Bundesliga": file_path_bundesliga,
    "La Liga": file_path_laliga,
    "Serie A": file_path_seriea,
    "Primeira Liga": file_path_primeiraliga,
    "Ligue 1": file_path_ligue1
}


def file_path_builder(var_league, var_firstseason, var_lastseason):

    # Verifica se a liga selecionada está no dicionário league_file_paths
    if var_league in league_file_paths:

        # Obtém o dicionário de caminhos de arquivo para a liga selecionada
        league_paths = league_file_paths[var_league]

        # Obtém as chaves (temporadas) do dicionário de caminhos de arquivo
        seasons = list(league_paths.keys())
        var_firstseason = int(var_firstseason)
        var_lastseason = int(var_lastseason)

        # Filtra as temporadas entre var_firstseason e var_lastseason
        selected_seasons = [season for season in seasons if var_firstseason <= int(season[-4:]) <= var_lastseason]

        # Inicializa a lista de caminhos de arquivo CSV
        csv_paths = []

        # Verifica se há temporadas filtradas
        if selected_seasons:
            # Itera sobre as temporadas filtradas
            for season in selected_seasons:
                # Adiciona o caminho do arquivo CSV da temporada atual à lista
                csv_paths.append(league_paths[season])

            # Retorna a lista de caminhos de arquivo CSV
            return csv_paths
        else:
            return None
    else:
        return None

