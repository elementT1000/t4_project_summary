import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import glob
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import MinMaxScaler
from collections import Counter


#Collect all of the .csv files
files = glob.glob('PGR_Dataset_1/*.csv')

def csv_label_filter(csv_file: str, planes, label_system: str):
    #Create dataframe from .csv
    df = pd.read_csv(csv_file, index_col=0, header=[0,1])
    pd.set_option('display.max_columns', None)
    #Take just the first 300 rows because these are the only ones that are labeeld
    df = df.head(300)

    angles = df.loc[:, df.columns.get_level_values(0).isin(planes)]
    angles.columns = angles.columns.droplevel(level=0)
    s_scaler = MinMaxScaler()
    scaled_angles = pd.DataFrame(s_scaler.fit_transform(angles), columns=angles.columns)
    scaled_angles = scaled_angles.fillna(0) #replacing nan with zeros to match live use case

    phase = df.filter(regex='Phase')
    phase.columns = phase.columns.droplevel(level=0)
    labels = phase.filter(regex=label_system)

    final = pd.concat([scaled_angles, labels], axis="columns")

    return final

#Set up a list to catch each processed dataframe
df_list = []

plns = ['Sagittal Plane Left', 'Sagittal Plane Right']
ls = 'LL - RunLab'

for i, f in enumerate(files, start=0):
    df = csv_label_filter(csv_file=f, planes=plns, label_system=ls)
    
    '''
    #This block is used to evaluate each .csv and make sure that the labels are consistent
    print("########################################################################################################")
    print(f)
    y = df.iloc[:, -1]
    counter1 = Counter(y)
    print("Number of items: " + str(len(counter1.items())))
    for key, value in counter1.items():
        per = value / len(y) * 100
        print('Class=%s, n=%d (%.2f%%)' % (key, value, per))
    '''

    #Add to list for concatenation later
    df_list.append(df)

master_df = pd.concat(df_list, axis=0, ignore_index=True)
#filename_planes = "_".join(plns)
filename = ls + "Double60_031423.csv"
print(filename + " is complete.")
master_df.to_csv("PGR_Dataset_1/training_sets/" + filename, index=False)
