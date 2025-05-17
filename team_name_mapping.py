# team_name_mapping.py
# This file contains mappings between different variations of team names
# Used to standardize team names across different data sources

# Serie A teams with variations (normalized_name: standard_name)
SERIE_A_TEAMS = {
    # Atalanta variations
    'atalanta': 'atalanta bc',
    'atalantabc': 'atalanta bc',
    'atalantabergamo': 'atalanta bc',
    'bergamo': 'atalanta bc',
    'dea': 'atalanta bc',
    
    # Roma variations
    'roma': 'as roma',
    'asroma': 'as roma',
    'giallorossi': 'as roma',
    'roma1927': 'as roma',
    
    # Inter variations
    'inter': 'inter milan',
    'intermilan': 'inter milan',
    'internazionale': 'inter milan',
    'fcinter': 'inter milan',
    'nerazzurri': 'inter milan',
    
    # Milan variations
    'milan': 'ac milan',
    'acmilan': 'ac milan',
    'rossoneri': 'ac milan',
    
    # Juventus variations
    'juventus': 'juventus',
    'juve': 'juventus',
    'juventusfc': 'juventus',
    'bianconeri': 'juventus',
    
    # Napoli variations
    'napoli': 'napoli',
    'sscnapoli': 'napoli',
    'naples': 'napoli',
    'partenopei': 'napoli',
    
    # Lazio variations
    'lazio': 'lazio',
    'sslazio': 'lazio',
    'biancocelesti': 'lazio',
    
    # Fiorentina variations
    'fiorentina': 'fiorentina',
    'acffiorentina': 'fiorentina',
    'viola': 'fiorentina',
    
    # Bologna variations
    'bologna': 'bologna',
    'bolognafc': 'bologna',
    'rossoblù': 'bologna',
    
    # Torino variations
    'torino': 'torino',
    'torinofc': 'torino',
    'toro': 'torino',
    'granata': 'torino',
    
    # Cagliari variations
    'cagliari': 'cagliari',
    'cagliaricalcio': 'cagliari',
    'isolani': 'cagliari',
    
    # Empoli variations
    'empoli': 'empoli',
    'empolifc': 'empoli',
    
    # Genoa variations
    'genoa': 'genoa',
    'genoafc': 'genoa',
    'grifone': 'genoa',
    
    # Lecce variations
    'lecce': 'lecce',
    'uslecce': 'lecce',
    'salentini': 'lecce',
    
    # Monza variations
    'monza': 'monza',
    'acmonza': 'monza',
    'biancorossi': 'monza',
    
    # Udinese variations
    'udinese': 'udinese',
    'udinesecalcio': 'udinese',
    'friuliani': 'udinese',
    
    # Venezia variations
    'venezia': 'venezia',
    'veneziafc': 'venezia',
    'lagunari': 'venezia',
    
    # Hellas Verona variations
    'verona': 'hellas verona',
    'hellasverona': 'hellas verona',
    'gialloblu': 'hellas verona',
    'hellas': 'hellas verona',
    
    # Como variations
    'como': 'como',
    'como1907': 'como',
    
    # Parma variations
    'parma': 'parma',
    'parmafc': 'parma',
    'ducali': 'parma'
}

# Premier League teams
PREMIER_LEAGUE_TEAMS = {
    'arsenal': 'arsenal',
    'gunners': 'arsenal',
    'astonvilla': 'aston villa',
    'villa': 'aston villa',
    'bournemouth': 'bournemouth',
    'afcbournemouth': 'bournemouth',
    'cherries': 'bournemouth',
    'brentford': 'brentford',
    'bees': 'brentford',
    'brighton': 'brighton',
    'brightonandhovealbion': 'brighton',
    'seagulls': 'brighton',
    'chelsea': 'chelsea',
    'blues': 'chelsea',
    'crystalpalace': 'crystal palace',
    'palace': 'crystal palace',
    'eagles': 'crystal palace',
    'everton': 'everton',
    'toffees': 'everton',
    'fulham': 'fulham',
    'cottagers': 'fulham',
    'ipswich': 'ipswich',
    'ipswichtown': 'ipswich',
    'tractorboys': 'ipswich',
    'leicester': 'leicester',
    'leicestercity': 'leicester',
    'foxes': 'leicester',
    'liverpool': 'liverpool',
    'reds': 'liverpool',
    'mancity': 'man city',
    'manchestercity': 'man city',
    'citizens': 'man city',
    'manutd': 'man united',
    'manchesterunited': 'man united',
    'reddevils': 'man united',
    'newcastle': 'newcastle',
    'newcastleunited': 'newcastle',
    'magpies': 'newcastle',
    'nottmforest': 'nott\'m forest',
    'nottinghamforest': 'nott\'m forest',
    'forest': 'nott\'m forest',
    'southampton': 'southampton',
    'saints': 'southampton',
    'tottenham': 'tottenham',
    'spurs': 'tottenham',
    'westham': 'west ham',
    'westhamunited': 'west ham',
    'hammers': 'west ham',
    'wolves': 'wolves',
    'wolverhamptonwanderers': 'wolves'
}

# La Liga teams
LA_LIGA_TEAMS = {
    'alaves': 'alaves',
    'deportivoalaves': 'alaves',
    'almeria': 'almeria',
    'udalmeria': 'almeria',
    'athletic': 'ath bilbao',
    'athleticbilbao': 'ath bilbao',
    'atletico': 'ath madrid',
    'atleticomadrid': 'ath madrid',
    'atleti': 'ath madrid',
    'barcelona': 'barcelona',
    'fcbarcelona': 'barcelona',
    'barca': 'barcelona',
    'celta': 'celta',
    'celtavigo': 'celta',
    'espanyol': 'espanol',
    'rcdespanyol': 'espanol',
    'getafe': 'getafe',
    'getafecf': 'getafe',
    'girona': 'girona',
    'gironafc': 'girona',
    'laspalmas': 'las palmas',
    'udlaspalmas': 'las palmas',
    'leganes': 'leganes',
    'cdleganes': 'leganes',
    'mallorca': 'mallorca',
    'rcamallorca': 'mallorca',
    'osasuna': 'osasuna',
    'caosasuna': 'osasuna',
    'rayo': 'vallecano',
    'rayovallecano': 'vallecano',
    'betis': 'betis',
    'realbetis': 'betis',
    'madrid': 'real madrid',
    'realmadrid': 'real madrid',
    'sociedad': 'sociedad',
    'realsociedad': 'sociedad',
    'sevilla': 'sevilla',
    'fcesevilla': 'sevilla',
    'valencia': 'valencia',
    'valenciacf': 'valencia',
    'villarreal': 'villarreal',
    'villarrealcf': 'villarreal'
}

# Bundesliga teams
BUNDESLIGA_TEAMS = {
    'augsburg': 'augsburg',
    'fcaugsburg': 'augsburg',
    'bayern': 'bayern munich',
    'bayernmunich': 'bayern munich',
    'fcbayern': 'bayern munich',
    'bochum': 'bochum',
    'vflbochum': 'bochum',
    'dortmund': 'dortmund',
    'borussiadortmund': 'dortmund',
    'bvb': 'dortmund',
    'gladbach': 'm\'gladbach',
    'borussiamgladbach': 'm\'gladbach',
    'borussia': 'm\'gladbach',
    'frankfurt': 'ein frankfurt',
    'eintrachtfrankfurt': 'ein frankfurt',
    'eintracht': 'ein frankfurt',
    'freiburg': 'freiburg',
    'scfreiburg': 'freiburg',
    'heidenheim': 'heidenheim',
    'fcheidenheim': 'heidenheim',
    'hoffenheim': 'hoffenheim',
    'tsg': 'hoffenheim',
    'kiel': 'holstein kiel',
    'holsteinkiel': 'holstein kiel',
    'mainz': 'mainz',
    'mainz05': 'mainz',
    'leipzig': 'rb leipzig',
    'rbleipzig': 'rb leipzig',
    'stpauli': 'st pauli',
    'fcstpauli': 'st pauli',
    'stuttgart': 'stuttgart',
    'vfbstuttgart': 'stuttgart',
    'unionberlin': 'union berlin',
    'fcunionberlin': 'union berlin',
    'werder': 'werder bremen',
    'werderbremen': 'werder bremen',
    'wolfsburg': 'wolfsburg',
    'vflwolfsburg': 'wolfsburg',
    'leverkusen': 'leverkusen',
    'bayerleverkusen': 'leverkusen',
    'bayer04': 'leverkusen'
}

# Ligue 1 teams
LIGUE_1_TEAMS = {
    'angers': 'angers',
    'scoangers': 'angers',
    'auxerre': 'auxerre',
    'aja': 'auxerre',
    'brest': 'brest',
    'stade brestois': 'brest',
    'lehavre': 'le havre',
    'lehavre': 'le havre',
    'havre': 'le havre',
    'lens': 'lens',
    'rclens': 'lens',
    'lille': 'lille',
    'losc': 'lille',
    'lyon': 'lyon',
    'olympiquelyon': 'lyon',
    'ol': 'lyon',
    'marseille': 'marseille',
    'olympiquemarseille': 'marseille',
    'om': 'marseille',
    'monaco': 'monaco',
    'asmonaco': 'monaco',
    'montpellier': 'montpellier',
    'mhsc': 'montpellier',
    'nantes': 'nantes',
    'fcnantes': 'nantes',
    'nice': 'nice',
    'ogcnice': 'nice',
    'paris': 'paris sg',
    'psg': 'paris sg',
    'parissaintgermain': 'paris sg',
    'reims': 'reims',
    'stadereims': 'reims',
    'rennes': 'rennes',
    'staderennais': 'rennes',
    'stetienne': 'st etienne',
    'saintetienne': 'st etienne',
    'asse': 'st etienne',
    'strasbourg': 'strasbourg',
    'racingstrasbourg': 'strasbourg',
    'rcsa': 'strasbourg',
    'toulouse': 'toulouse',
    'tfc': 'toulouse'
}

# Primeira Liga teams
PRIMEIRA_LIGA_TEAMS = {
    'arouca': 'arouca',
    'fcarouca': 'arouca',
    'avs': 'avs',
    'cdaves': 'avs',
    'benfica': 'benfica',
    'slbenfica': 'benfica',
    'boavista': 'boavista',
    'boavistafc': 'boavista',
    'braga': 'sp braga',
    'sporting braga': 'sp braga',
    'scbraga': 'sp braga',
    'casapia': 'casa pia',
    'casapiaac': 'casa pia',
    'estoril': 'estoril',
    'estorilpraia': 'estoril',
    'estrela': 'estrela',
    'estrelaamadora': 'estrela',
    'famalicao': 'famalicao',
    'fcfamalicao': 'famalicao',
    'farense': 'farense',
    'scfarense': 'farense',
    'gilvicente': 'gil vicente',
    'gilvicente': 'gil vicente',
    'moreirense': 'moreirense',
    'moreiren': 'moreirense',
    'nacional': 'nacional',
    'cdnacional': 'nacional',
    'porto': 'porto',
    'fcporto': 'porto',
    'dragons': 'porto',
    'rioave': 'rio ave',
    'rioavefc': 'rio ave',
    'santaclara': 'santa clara',
    'cdsantaclara': 'santa clara',
    'sporting': 'Sp Lisbon',
    'sportinglisbon': 'Sp Lisbon',
    'sportingcp': 'Sp Lisbon',
    'guimaraes': 'Guimaraes',
    'vitoriasc': 'Guimaraes',
    'vitoriaganmarares': 'Guimaraes',
    'sportinglisbon': 'Sp Lisbon',  # Handle spaces being removed during normalization
    'vitóriasc': 'Guimaraes',       # Handle accent characters
    'vitoriasc': 'Guimaraes',       # Handle missing accents
}

# Combined dictionary of all teams
TEAM_MAPPINGS = {
    **SERIE_A_TEAMS,
    **PREMIER_LEAGUE_TEAMS,
    **LA_LIGA_TEAMS,
    **BUNDESLIGA_TEAMS,
    **LIGUE_1_TEAMS,
    **PRIMEIRA_LIGA_TEAMS
}

# Mapping of league names to league codes for The Odds API
LEAGUE_API_MAPPING = {
    'Serie A': 'soccer_italy_serie_a',
    'Premier League': 'soccer_epl',
    'La Liga': 'soccer_spain_la_liga', 
    'Bundesliga': 'soccer_germany_bundesliga',
    'Ligue 1': 'soccer_france_ligue_one',
    'Primeira Liga': 'soccer_portugal_primeira_liga'
}

# Bookmaker name mappings (API name to CSV column prefix)
BOOKMAKER_MAPPINGS = {
    'bet365': 'B365',
    'bwin': 'BW',
    'betclic': 'BTC',
    'betano': 'BT',
    'unibet': 'UB',
    'williamhill': 'WH',
    'pinnacle': 'PS'
}

def normalize_team_name(team_name):
    """
    Normalize a team name by removing spaces, special characters, and converting to lowercase.
    
    Args:
        team_name (str): The team name to normalize
        
    Returns:
        str: The normalized team name
    """
    if not team_name:
        return ""
    # Remove non-alphanumeric characters and convert to lowercase
    normalized = ''.join(c.lower() for c in team_name if c.isalnum())
    return normalized

def get_standard_team_name(team_name):
    """
    Get the standard team name from a team name or its variation.
    
    Args:
        team_name (str): The team name to standardize
        
    Returns:
        str: The standard team name, or the original name if not found
    """
    normalized = normalize_team_name(team_name)
    return TEAM_MAPPINGS.get(normalized, team_name)

def get_teams_for_league(league_name):
    """
    Get a dictionary of team mappings for a specific league.
    
    Args:
        league_name (str): The league name
        
    Returns:
        dict: Dictionary of team mappings for the specified league
    """
    if league_name == "Serie A":
        return SERIE_A_TEAMS
    elif league_name == "Premier League":
        return PREMIER_LEAGUE_TEAMS
    elif league_name == "La Liga":
        return LA_LIGA_TEAMS
    elif league_name == "Bundesliga":
        return BUNDESLIGA_TEAMS
    elif league_name == "Ligue 1":
        return LIGUE_1_TEAMS
    elif league_name == "Primeira Liga":
        return PRIMEIRA_LIGA_TEAMS
    else:
        return {}

def get_sport_key(league_name):
    """
    Get the API sport key for the given league name.
    
    Args:
        league_name (str): The league name
        
    Returns:
        str: The API sport key for the league
    """
    return LEAGUE_API_MAPPING.get(league_name, 'soccer_italy_serie_a')

def get_bookmaker_code(bookmaker_name):
    """
    Get the bookmaker code for the given bookmaker name.
    
    Args:
        bookmaker_name (str): The bookmaker name
        
    Returns:
        str: The bookmaker code
    """
    return BOOKMAKER_MAPPINGS.get(bookmaker_name.lower(), '')