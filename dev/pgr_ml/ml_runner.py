import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import joblib


file = 'CN 7-6-2022 Sagittal.csv'
path = 'C:/Users/trott/PycharmProjects/posetracking/ProcessedVideos/' + file

def ml_runner(csv_path):
    df = pd.read_csv(path)
    pd.set_option('display.max_columns', None)

    #store_frame = df.filter(regex='Frame')
    #df.drop(['Frame', 'Time(s)'], axis=1, inplace=True)

    #adjust scaler to make inquiries into divergent results
    s_scaler = MinMaxScaler()
    df = pd.DataFrame(s_scaler.fit_transform(df), columns=df.columns)

    #print(df)
    #print(df.shape)

    #load the model and predict
    loaded_model = joblib.load('extratreestrainedmodel.sav')
    result = loaded_model.predict(df)
    df_results = pd.DataFrame(result, columns=[('Phase', 'RL - RunLab')])

    #The labelencoding tool labels the classes in alphabetical order, so need to decode as such
    df_results.loc[(df_results.Phase == 0), 'Phase'] = 'Initial Strike'
    df_results.loc[(df_results.Phase == 1), 'Phase'] = 'Initial Swing'
    df_results.loc[(df_results.Phase == 2), 'Phase'] = 'Loading Response'
    df_results.loc[(df_results.Phase == 3), 'Phase'] = 'Midstance'
    df_results.loc[(df_results.Phase == 4), 'Phase'] = 'Midswing'
    df_results.loc[(df_results.Phase == 5), 'Phase'] = 'Terminal Stance'
    df_results.loc[(df_results.Phase == 6), 'Phase'] = 'Terminal Swing'
    df_results.loc[(df_results.Phase == 6), 'Phase'] = 'Toe Off'

    print(df_results)
    #print(type(df_results))

    df_angles = pd.DataFrame(s_scaler.inverse_transform(df), columns=df.columns)

    concat_result = pd.concat([df_angles, df_results], axis='columns')
    print(concat_result)

    final = pd.concat([store_frame, concat_result], axis='columns')

    filename = 'predicted ' + file
    final.to_csv('C:/Users/trott/PycharmProjects/posetracking/ProcessedVideos/' + filename, index=False)
