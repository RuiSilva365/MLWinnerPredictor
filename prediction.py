import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
import treatment


def preparePrediction(star_club,opp_club):
    #df1
    df1 = pd.read_csv("TeamGames.csv")
    df1 = treatment.replace_ftr(df1, star_club)
    df1 = treatment.replace_club_names_with_indices(df1, star_club, opp_club)
    df1 = df1.drop(columns=["Div"])
    df1 = treatment.treatmentofDate(df1)
    pd.set_option('display.max_columns', None)
    df1.dropna(inplace=True)
    print(("\n\n\n\tJOGOS DA EQUIPA1\t\n\n"))
    print(df1.to_string(index=False))

    #df2
    df2 = pd.read_csv("OppGames.csv")
    df2 = treatment.replace_ftr(df2, opp_club)
    df2 = treatment.replace_club_names_with_indices(df2, star_club, opp_club)
    df2 = df2.drop(columns=["Div"])
    df2 = treatment.treatmentofDate(df2)
    pd.set_option('display.max_columns', None)
    df2.dropna(inplace=True)
    print(("\n\n\n\tJOGOS DA EQUIPA2\t\n\n"))
    print(df2.to_string(index=False))
    df_merged = pd.concat([df1, df2])
    print(("\n\n\n\tJOGOS AMBAS EQUIPAS\t\n\n"))
    print(df_merged.to_string(index=False))
    df_merged.to_csv("BothTeams.csv")
    return df_merged

def preprocess_data(df, columns_to_keep):
    # Normalização dos dados

    scaler = StandardScaler()
    df_scaled = pd.DataFrame(scaler.fit_transform(df[columns_to_keep]), columns=columns_to_keep)
    return df_scaled, scaler

def load_and_preprocess_next_game_data(scaler, columns_to_keep):
    next_game_data = pd.read_csv('NextGame.csv')
    next_game_data_scaled = pd.DataFrame(scaler.transform(next_game_data[columns_to_keep]), columns=columns_to_keep)
    return next_game_data_scaled

def getOddsProbability():
    columns_to_keep = ['B365H', 'BWH', 'MaxH', 'AvgH']
    next_game_data = pd.read_csv('NextGame.csv')
    odds_H = next_game_data[columns_to_keep].iloc[0]
    probabilidades = [1 / odd for odd in odds_H]
    probabilidade_media = sum(probabilidades) / len(probabilidades)
    return probabilidade_media * 100  # Em percentual

def getPrediction(df, club, opp):
    columns_to_keep = [col for col in df.columns if col not in ['FTHG', 'Dia_da_Semana', 'FTAG', 'FTR', 'Max>2.5.1', 'Day', 'Month', 'Day_of_week']]
    y = df['FTR']
    X = df[columns_to_keep]
    next_game_data = pd.read_csv('NextGame.csv')
    next_game_data = next_game_data[columns_to_keep]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.4, random_state=42)
    model = LogisticRegression(max_iter=10000)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print("Acurácia de teste modelo de regressão logística:", accuracy)
    y_prob = model.predict_proba(next_game_data)
    club1_win_prob = y_prob[:, 1].mean()
    print("X_TRAIN\n")
    print(X_train.to_string(index=False))
    print("X_TEST\n")
    print( X_test.to_string(index=False))
    print("NEXT_GAME_DATA_SCALED\n")
    print(next_game_data.to_string(index=False))
    return club1_win_prob * 100

def sigmoid(x):
    return 1 / (1 + np.exp(-x))

def getLinearPrediction(df, club, opp):
    columns_to_keep = ['B365H', 'B365D', 'B365A', 'BWH', 'BWD', 'BWA', 'MaxH', 'MaxD', 'MaxA', 'AvgH', 'AvgD', 'AvgA']
    y = df['FTR']
    X_scaled, scaler = preprocess_data(df, columns_to_keep)
    next_game_data_scaled = load_and_preprocess_next_game_data(scaler, columns_to_keep)
    X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.4, random_state=42)
    model = LinearRegression()
    model.fit(X_train, y_train)
    accuracy = model.score(X_test, y_test)
    print("Test accuracy of linear regression model:", accuracy)
    club1_win_prob = sigmoid(model.predict(next_game_data_scaled)).mean()
    return club1_win_prob * 100

def getGradientBoostingClassifierPrediction(df, club, opp):
    columns_to_keep = [col for col in df.columns if col not in ['FTHG', 'Dia_da_Semana', 'FTAG', 'FTR', 'Max>2.5.1', 'Day', 'Month', 'Day_of_week']]
    y = df['FTR']
    X_scaled, scaler = preprocess_data(df, columns_to_keep)
    next_game_data_scaled = load_and_preprocess_next_game_data(scaler, columns_to_keep)
    X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.4, random_state=42)
    gbm_model = GradientBoostingClassifier()
    gbm_model.fit(X_train, y_train)
    gbm_pred = gbm_model.predict(X_test)
    gbm_accuracy = accuracy_score(y_test, gbm_pred)
    print("Acurácia de teste Gradient Boosting:", gbm_accuracy)
    gbm_win_prob = gbm_model.predict_proba(next_game_data_scaled)[:, 1].mean()
    return gbm_win_prob * 100

def getRandomForestClassifierPrediction(df, club, opp):
    columns_to_keep = [col for col in df.columns if col not in ['FTHG', 'Dia_da_Semana', 'FTAG', 'FTR', 'Max>2.5.1','Day', 'Month', 'Day_of_week']]
    y = df['FTR']
    X_scaled, scaler = preprocess_data(df, columns_to_keep)
    next_game_data_scaled = load_and_preprocess_next_game_data(scaler, columns_to_keep)
    X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.4, random_state=42)
    rf_model = RandomForestClassifier()
    rf_model.fit(X_train, y_train)
    rf_pred = rf_model.predict(X_test)
    rf_accuracy = accuracy_score(y_test, rf_pred)
    print("Acurácia de teste Random Forest:", rf_accuracy)
    rf_win_prob = rf_model.predict_proba(next_game_data_scaled)[:, 1].mean()
    return rf_win_prob * 100

def getSVMClassifierPrediction(df, club, opp):
    columns_to_keep = [col for col in df.columns if col not in ['FTHG', 'Dia_da_Semana', 'FTAG', 'FTR', 'Max>2.5.1']]
    y = df['FTR']
    X_scaled, scaler = preprocess_data(df, columns_to_keep)
    next_game_data_scaled = load_and_preprocess_next_game_data(scaler, columns_to_keep)
    X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.4, random_state=42)
    svm_model = SVC(probability=True)
    svm_model.fit(X_train, y_train)
    svm_pred = svm_model.predict(X_test)
    svm_accuracy = accuracy_score(y_test, svm_pred)
    print("Acurácia de teste SVM:", svm_accuracy)
    svm_win_prob = svm_model.predict_proba(next_game_data_scaled)[:, 1].mean()
    return svm_win_prob * 100

def getDecisionTreeClassifierPrediction(df, club, opp):
    columns_to_keep = [col for col in df.columns if col not in ['FTHG', 'Dia_da_Semana', 'FTAG', 'FTR', 'Max>2.5.1']]
    y = df['FTR']
    X_scaled, scaler = preprocess_data(df, columns_to_keep)
    next_game_data_scaled = load_and_preprocess_next_game_data(scaler, columns_to_keep)
    X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.4, random_state=42)
    dt_model = DecisionTreeClassifier()
    dt_model.fit(X_train, y_train)
    dt_pred = dt_model.predict(X_test)
    dt_accuracy = accuracy_score(y_test, dt_pred)
    print("Acurácia de teste Decision Tree:", dt_accuracy)
    dt_win_prob = dt_model.predict_proba(next_game_data_scaled)[:, 1].mean()
    return dt_win_prob * 100

def getNeuralNetworkPrediction(df, club, opp):
    columns_to_keep = [col for col in df.columns if col not in ['FTHG', 'Dia_da_Semana', 'FTAG', 'FTR', 'Max>2.5.1', 'Day', 'Month', 'Day_of_week']]
    y = df['FTR']
    X_scaled, scaler = preprocess_data(df, columns_to_keep)
    next_game_data_scaled = load_and_preprocess_next_game_data(scaler, columns_to_keep)
    X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.4, random_state=42)
    nn_model = MLPClassifier(hidden_layer_sizes=(145, 70), max_iter=1000)
    nn_model.fit(X_train, y_train)
    nn_pred = nn_model.predict(X_test)
    nn_accuracy = accuracy_score(y_test, nn_pred)
    print("Acurácia de teste Rede Neural:", nn_accuracy)
    print("X_TRAIN\n")
    print(X_train.to_string(index=False))
    print("X_TEST\n")
    print( X_test.to_string(index=False))
    print("NEXT_GAME_DATA_SCALED\n")
    print(next_game_data_scaled.to_string(index=False))
    nn_win_prob = nn_model.predict_proba(next_game_data_scaled)[:, 1].mean()
    return nn_win_prob * 100
