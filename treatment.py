from datetime import datetime
from telnetlib import EC
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions
import pandas as pd
import url
#VARIAVEIS DO CSV
# Div: Divisão da liga (por exemplo, E0 para a Premier League da Inglaterra, SP1 para La Liga da Espanha).
# Date: Data da partida.
# Time: Hora da partida.
# HomeTeam: Time da casa.
# AwayTeam: Time visitante.
# FTHG: Gols marcados pelo time da casa (em tempo integral).
# FTAG: Gols marcados pelo time visitante (em tempo integral).
# FTR: Resultado em tempo integral (H para casa, A para fora, D para empate).
# HTHG: Gols marcados pelo time da casa (no intervalo).
# HTAG: Gols marcados pelo time visitante (no intervalo).
# HTR: Resultado no intervalo (H para casa, A para fora, D para empate).
# HS: Chutes do time da casa.
# AS: Chutes do time visitante.
# HST: Chutes no alvo do time da casa.
# AST: Chutes no alvo do time visitante.
# HF: Faltas cometidas pelo time da casa.
# AF: Faltas cometidas pelo time visitante.
# HC: Chutes de canto do time da casa.
# AC: Chutes de canto do time visitante.
# HY: Cartões amarelos do time da casa.
# AY: Cartões amarelos do time visitante.
# HR: Cartões vermelhos do time da casa.
# AR: Cartões vermelhos do time visitante.
# B365H: Cotações da Bet365 para a vitória do time da casa.
# B365D: Cotações da Bet365 para o empate.
# B365A: Cotações da Bet365 para a vitória do time visitante.
# BWH: Cotações da BetWay para a vitória do time da casa.
# BWD: Cotações da BetWay para o empate.
# BWA: Cotações da BetWay para a vitória do time visitante.
# IWH: Cotações da Interwetten para a vitória do time da casa.
# IWD: Cotações da Interwetten para o empate.
# IWA: Cotações da Interwetten para a vitória do time visitante.
# PSH: Cotações da Pinnacle Sports para a vitória do time da casa.
# PSD: Cotações da Pinnacle Sports para o empate.
# PSA: Cotações da Pinnacle Sports para a vitória do time visitante.
# WHH: Cotações da William Hill para a vitória do time da casa.
# WHD: Cotações da William Hill para o empate.
# WHA: Cotações da William Hill para a vitória do time visitante.
# VCH: Cotações da VC Bet para a vitória do time da casa.
# VCD: Cotações da VC Bet para o empate.
# VCA: Cotações da VC Bet para a vitória do time visitante.
# MaxH: Cotações máximas para a vitória do time da casa.
# MaxD: Cotações máximas para o empate.
# MaxA: Cotações máximas para a vitória do time visitante.
# AvgH: Cotações médias para a vitória do time da casa.
# AvgD: Cotações médias para o empate.
# AvgA: Cotações médias para a vitória do time visitante.
# B365>2.5: Cotações da Bet365 para Mais de 2.5 gols.
# B365<2.5: Cotações da Bet365 para Menos de 2.5 gols.
# P>2.5: Probabilidades implícitas para Mais de 2.5 gols.
# P<2.5: Probabilidades implícitas para Menos de 2.5 gols.
# Max>2.5: Cotações máximas para Mais de 2.5 gols.
# Max<2.5: Cotações máximas para Menos de 2.5 gols.
# Avg>2.5: Cotações médias para Mais de 2.5 gols.
# Avg<2.5: Cotações médias para Menos de 2.5 gols.
# AHh: Handicap asiático.
# B365AHH: Cotações da Bet365 para Handicap asiático da equipe da casa.
# B365AHA: Cotações da Bet365 para Handicap asiático da equipe visitante.
# PAHH: Probabilidades implícitas para Handicap asiático da equipe da casa.
# PAHA: Probabilidades implícitas para Handicap asiático da equipe visitante.
# MaxAHH: Cotações máximas para Handicap asiático da equipe da casa.
# MaxAHA: Cotações máximas para Handicap asiático da equipe visitante.
# AvgAHH: Cotações médias para Handicap asiático da equipe da casa.
# AvgAHA: Cotações médias para Handicap asiático da equipe visitante.
# B365CH: Cotações da Bet365 para vitória da equipe da casa (com handicap).
# B365CD: Cotações da Bet365 para empate (com handicap).
# B365CA: Cotações da Bet365 para vitória da equipe visitante (com handicap).
# BWCH: Cotações da BetWay para vitória da equipe da casa (com handicap).
# BWCD: Cotações da BetWay para empate (com handicap).
# BWCA: Cotações da BetWay para vitória da equipe visitante (com handicap).
# IWCH: Cotações da Interwetten para vitória da equipe da casa (com handicap).
# IWCD: Cotações da Interwetten para empate (com handicap).
# IWCA: Cotações da Interwetten para vitória da equipe visitante (com handicap).
# PSCH: Cotações da Pinnacle Sports para vitória da equipe da casa (com handicap).
# PSCD: Cotações da Pinnacle Sports para empate (com handicap).
# PSCA: Cotações da Pinnacle Sports para vitória da equipe visitante (com handicap).
# WHCH: Cotações da William Hill para vitória da equipe da casa (com handicap).
# WHCD: Cotações da William Hill para empate (com handicap).
# WHCA: Cotações da William Hill para vitória da equipe visitante (com handicap).
# VCCH: Cotações da VC Bet para vitória da equipe da casa (com handicap).
# VCCD: Cotações da VC Bet para empate (com handicap).
# VCCA: Cotações da VC Bet para vitória da equipe visitante (com handicap).
# MaxCH: Cotações máximas para vitória da equipe da casa (com handicap).
# MaxCD: Cotações máximas para empate (com handicap).
# MaxCA: Cotações máximas para vitória da equipe visitante (com handicap).
# AvgCH: Cotações médias para vitória da equipe da casa (com handicap).
# AvgCD: Cotações médias para empate (com handicap).
# AvgCA: Cotações médias para vitória da equipe visitante (com handicap).
# B365C>2.5: Cotações da Bet365 para vitória da equipe da casa (com mais de 2.5 gols).
# B365C<2.5: Cotações da Bet365 para vitória da equipe da casa (com menos de 2.5 gols).
# PC>2.5: Probabilidades implícitas para vitória da equipe da casa (com mais de 2.5 gols).
# PC<2.5: Probabilidades implícitas para vitória da equipe da casa (com menos de 2.5 gols).
# MaxC>2.5: Cotações máximas para vitória da equipe da casa (com mais de 2.5 gols).
# MaxC<2.5: Cotações máximas para vitória da equipe da casa (com menos de 2.5 gols).
# AvgC>2.5: Cotações médias para vitória da equipe da casa (com mais de 2.5 gols).
# AvgC<2.5: Cotações médias para vitória da equipe da casa (com menos de 2.5 gols).
# AHCh: Handicap asiático para a equipe da casa.
# B365CAHH: Cotações da Bet365 para Handicap asiático da equipe da casa.
# B365CAHA: Cotações da Bet365 para Handicap asiático da equipe visitante.
# PCAHH: Probabilidades implícitas para Handicap asiático da equipe da casa.
# PCAHA: Probabilidades implícitas para Handicap asiático da equipe visitante.
# MaxCAHH: Cotações máximas para Handicap asiático da equipe da casa.
# MaxCAHA: Cotações máximas para Handicap asiático da equipe visitante.
# AvgCAHH: Cotações médias para Handicap asiático da equipe da casa.
# AvgCAHA: Cotações médias para Handicap asiático da equipe visitante.

def handler(season, star_league, star_club, opp_club):
    pd.set_option('display.max_columns', None)
    columns_remove = ['PSD', 'PSA']

    dfs_club = []  # List to hold DataFrames for the star club
    dfs_opp = []  # List to hold DataFrames for the opponent club

    # Converte a temporada para inteiro
    var_firstseason = int(season)
    var_lastseason = 2324

    if star_league in url.file_path_leagues:
        csvs_path = url.file_path_builder(star_league, var_firstseason, var_lastseason)

        for path in csvs_path:
            df = cut_useless_rows(path)

            # Processando para star_club
            df_club = filter_club_games(star_club, df)
            dfs_club.append(df_club)

            # Processando para opp_club
            df_opp = filter_club_games(opp_club, df)
            dfs_opp.append(df_opp)

        # Concatenate all DataFrames
        df_club_concatenated = pd.concat(dfs_club)
        df_opp_concatenated = pd.concat(dfs_opp)

        # Save to CSV
        df_club_concatenated.to_csv("TeamGames.csv", index=False)
        df_opp_concatenated.to_csv("OppGames.csv", index=False)

        return None  # No error message
    else:
        return 404


#fazer o drop dos NaN e de colunas que não se vai usar
def cut_useless_rows(file):
    # Ler o arquivo CSV
    df = pd.read_csv(file,index_col=0)

    if df is None:
        print("Erro: DataFrame de entrada é nulo.")
        return None

    # Remover linhas com valores nulos
    df.dropna(inplace=True)

    # Lista de colunas a serem mantidas
    columns_to_keep = ['Date',  'HomeTeam', 'AwayTeam', 'FTHG', 'FTAG',
                       'FTR', 'B365H', 'B365D', 'B365A', 'BWH', 'BWD', 'BWA', 'MaxH', 'MaxD', 'MaxA', 'AvgH',
                        'AvgD', 'AvgA', 'B365>2.5', 'B365<2.5', 'Max>2.5',
                       'Max<2.5', 'Max>2.5', 'Avg<2.5', 'Avg>2.5']

    # Verifica se as colunas a serem mantidas existem no DataFrame
    missing_columns = [col for col in columns_to_keep if col not in df.columns]
    if missing_columns:
        return None

    # Selecionar apenas as colunas desejadas
    df_selected = df[columns_to_keep].copy()  # Create a copy to avoid SettingWithCopyWarning

    # Adicionar a coluna 'Dia_da_Semana' usando .loc para evitar SettingWithCopyWarning
    df_selected.loc[:, 'Dia_da_Semana'] = df_selected['Date'].apply(getDayofWeek)

    # Retorna o DataFrame modificado
    return df_selected
#filtrar os jogos de um clube especifico
def filter_club_games(var_club_name, df):
    if df is None:  # Adicionei essa verificação para evitar erros quando o DataFrame é None
        return None
    df = df.loc[(df['HomeTeam'] == var_club_name) | (df['AwayTeam'] == var_club_name)]
    return df

#função para ver como estão os nomes das equipas nos csvs
def filter_clubs_names():
    df = pd.read_csv("https://www.football-data.co.uk/mmz4281/2324/I1.csv")
    club_names = df['HomeTeam'].unique()
    for name in club_names:
        print(name)

def finalscore_and_teams(df):
    # Seleciona apenas as colunas desejadas
    selected_columns = ['HomeTeam', 'AwayTeam', 'FTHG', 'FTAG']
    new_df = df[selected_columns].copy()
    return new_df

def data_treatmentP(file):
    df = pd.read_csv(file)
    if df is None:
        print("Erro: DataFrame de entrada é nulo.")
        return None
    df.dropna(inplace=True)
    columns_to_remove = [
        'Div', 'FTR', 'HTAG', 'HTR', 'HS', 'AS', 'HST', 'AST', 'HF', 'AF', 'HC', 'AC', 'HY',
        'AY',
        'HR', 'AR', 'IWH', 'IWD', 'IWA', 'PSH', 'PSD', 'PSA', 'WHH', 'WHD', 'WHA', 'VCH', 'VCD', 'VCA', 'B365AHH', 'B365AHA',
        'PAHH', 'PAHA', 'MaxAHH', 'MaxAHA', 'AvgAHH', 'AvgAHA',  'B365AHH',
        'B365AHA', 'PAHH', 'PAHA', 'MaxAHH', 'MaxAHA', 'AvgAHH', 'AvgAHA', 'B365CH', 'B365CD', 'B365CA', 'BWCH', 'BWCD',
        'BWCA', 'IWCH', 'IWCD', 'IWCA', 'PSCH', 'PSCD', 'PSCA', 'WHCH', 'WHCD', 'WHCA', 'VCCH', 'VCCD', 'VCCA'
    ]
    # Verifica se as colunas a serem removidas existem no DataFrame
    missing_columns = [col for col in columns_to_remove if col not in df.columns]
    if missing_columns:
        print(f"Erro: As seguintes colunas não existem no DataFrame: {', '.join(missing_columns)}")
        return None

    # Drop das colunas
    df.drop(columns=columns_to_remove, inplace=True)

    # Retorna o DataFrame modificado
    return df


def getDate(df_team):
    game_date = df_team["Date"]
    return game_date

def treatmentofDate(df):
    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'], format='%d/%m/%Y', dayfirst=True)

        # Extract day, month, and day of the week into new columns
        df['Day'] = df['Date'].dt.day
        df['Month'] = df['Date'].dt.month
        df['Day_of_week'] = df['Date'].dt.dayofweek  # 0 for Monday, 1 for Tuesday, etc.

        # Remove the original "Date" column
        df.drop(columns=['Date'], inplace=True)
    return df
def getDayofWeek(data):
    # Converter a string de data para um objeto datetime
    data_object = datetime.strptime(data, '%d/%m/%Y')  # Usar '%d/%m/%Y' para ano com quatro dígitos

    # Obter o dia da semana como um número (0 = segunda-feira, 1 = terça-feira, ..., 6 = domingo)
    day_of_the_week_num = data_object.weekday()

    # Mapear o número do dia da semana para o nome do dia
    #week_days = ['Segunda-feira', 'Terça-feira', 'Quarta-feira', 'Quinta-feira', 'Sexta-feira', 'Sábado', 'Domingo']
    #week_day_name = week_days[day_of_the_week_num]

    return day_of_the_week_num


def replace_club_names_with_indices(df, star_club, opp_club):
    # Carregar o DataFrame a partir do arquivo CSV
    reverse_clubs = {}
    for league, clubs in url.clubs_by_league.items():
        for idx, club in enumerate(clubs, start=1):
            reverse_clubs[club] = idx

    # Substituindo os nomes dos clubes pelos índices
    df["HomeTeam"] = df["HomeTeam"].apply(lambda x: 99.0 if x == star_club else (98.0 if x == opp_club else reverse_clubs.get(x)))
    df["AwayTeam"] = df["AwayTeam"].apply(lambda x: 99.0 if x == star_club else (98.0 if x == opp_club else reverse_clubs.get(x)))
    return df




def replace_ftr(df, selected_team):
    # Mapear os valores da coluna "FTR" com base na equipe selecionada, 1se ganha 0 o resto
    df['FTR'] = df.apply(lambda row: 1 if (row['FTR'] == 'H' and row['HomeTeam'] == selected_team) or
                                          (row['FTR'] == 'A' and row['AwayTeam'] == selected_team) else 0, axis=1)
    return df


def replace_ftr3(df, selected_team):
    # Map the values of the column "FTR" based on the selected team
    # 1 = Victory for the selected team
    # 0 = Draw
    # 2 = Defeat for the selected team

    df['FTR'] = df.apply(lambda row: 1 if (row['FTR'] == 'H' and row['HomeTeam'] == selected_team) or
                                          (row['FTR'] == 'A' and row['AwayTeam'] == selected_team) else
    (2 if (row['FTR'] == 'H' and row['AwayTeam'] == selected_team) or
          (row['FTR'] == 'A' and row['HomeTeam'] == selected_team) else 0), axis=1)
    return df
def getNextgameData(url):
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')

    # Initialize the WebDriver
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)

    # Open the URL
    driver.get(url)

    # Initialize explicit wait
    wait = WebDriverWait(driver, 20)
    odds_data = {}

    try:
        # Wait for the page to load
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))

        # Click the reject all cookies button if present
        try:
            cookie_button = wait.until(
                EC.element_to_be_clickable((By.XPATH, ".//button[@id='onetrust-reject-all-handler']")))
            cookie_button.click()
            print("Cookie reject button clicked.")
        except:
            print("Cookie reject button not found or already clicked.")

        # Wait for the odds elements to be present
        print("Waiting for the odds elements to be present...")
        odds_elements = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//p[@class='height-content']")))

        # Extract the text of each relevant odds element
        odds_values = [element.text for element in odds_elements]
        print(f"Odds values: {odds_values}")

        # Map the odds values to their respective labels
        if len(odds_values) >= 34:
            odds_data = {
                'B365H': odds_values[0],
                'B365D': odds_values[1],
                'B365A': odds_values[2],
                'BWH': odds_values[3],
                'BWD': odds_values[4],
                'BWA': odds_values[5],
                'MaxH': odds_values[31],
                'MaxD': odds_values[32],
                'MaxA': odds_values[33],
                'AvgH': odds_values[27],
                'AvgD': odds_values[28],
                'AvgA': odds_values[29]
            }

    except Exception as e:
        print(f"An error occurred: {e}")
        # Log page source for debugging
        with open("page_source.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)

    finally:
        driver.quit()

    return odds_data


def transform_url(url):
    # Verifica se o URL contém "1X2"
    if "#1X2" in url:
        # Divide o URL pela parte do marcador "#"
        base_url, params = url.split("#")

        # Extrai os componentes do parâmetro
        match_params = params.split(";")
        match_id = match_params[0]

        # Cria o novo URL com o formato "over-under"
        new_url = f"{base_url}#over-under;{match_id};2.50;0"
        return new_url
    else:
        return url  # Retorna o URL original se não for do tipo "1X2"
def getNextgameGoalsData(url):
    url = transform_url(url)
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')

    # Inicializar o WebDriver
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)

    # Abrir o URL
    driver.get(url)

    # Inicializar espera explícita
    wait = WebDriverWait(driver, 20)
    odds_data = {}

    try:
        # Aguardar o carregamento da página
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))

        # Clicar no botão para rejeitar todos os cookies, se presente
        try:
            cookie_button = wait.until(EC.element_to_be_clickable((By.XPATH, ".//button[@id='onetrust-reject-all-handler']")))
            cookie_button.click()
            print("Cookie reject button clicked.")
        except:
            print("Cookie reject button not found or already clicked.")

        # Esperar pelos elementos de odds estarem presentes
        print("Waiting for the odds elements to be present...")
        odds_elements = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//p[@class='height-content']")))

        # Extrair o texto de cada elemento de odds relevante
        odds_values = [element.text for element in odds_elements]
        print(f"Odds values: {odds_values}")

        # Mapear os valores de odds para suas respectivas labels
        if len(odds_values) >= 21:
            odds_data = {
                'B365>2.5': odds_values[0],
                'B365<2.5': odds_values[1],
                'Max<2.5': odds_values[9],
                'Max>2.5': odds_values[10],
                'Avg<2.5': odds_values[6],
                'Avg>2.5': odds_values[8]
            }


    except Exception as e:
        print(f"An error occurred: {e}")
        # Registrar o código fonte da página para depuração
        with open("page_source.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)

    finally:
        driver.quit()

    return odds_data


# getNexgameData('https://www.oddsportal.com/football/portugal/liga-portugal/braga-fc-porto-t4RTDzCR/#1X2;2')
#transform_url('https://www.oddsportal.com/football/portugal/liga-portugal/braga-fc-porto-t4RTDzCR/#1X2;2')