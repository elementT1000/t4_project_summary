import numpy as np
import pandas as pd
from collections import Counter

import imblearn
from imblearn.over_sampling import SMOTE
from imblearn.under_sampling import RandomUnderSampler
from imblearn.pipeline import Pipeline

from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import RepeatedStratifiedKFold
from sklearn.model_selection import GridSearchCV
from sklearn.impute import KNNImputer

from sklearn.metrics import classification_report, confusion_matrix, f1_score
import joblib


df = pd.read_csv(r'PGR_Dataset_1\training_sets\LL - RunLabDouble60_031423.csv')
print("Pre-drop")
print(df.shape)

# get rid of error frames b/c they do not reflect reality
df_no_error = df[df.iloc[:, -1] != 'error']
df_clean = df_no_error.fillna(0)
print("Post-drop")
print(df_clean.shape)

# Seperate the dependent and independent variables
df_clean.columns = df_clean.columns.str.strip()
y = df_clean.iloc[:, -1]
X = df_clean.drop(df_clean.columns[-1], axis=1)

# Numerically encode the target variables
le = LabelEncoder()
y_enc = le.fit_transform(y)

counter1 = Counter(y)
for key, value in counter1.items():
    per = value / len(y) * 100
    print('Class=%s, n=%d (%.2f%%)' % (key, value, per))

# Split the dataset into train and test groups, 90/10 ratio
X_train, X_test, y_train, y_test = train_test_split(X, y_enc, test_size=0.10, random_state=42)

'''#Use a knn imputer to fill in blanks in the data
#This may be making bad data
knn_imputer = KNNImputer(n_neighbors=5)
#fit it to the data
knn_imputer.fit(X_train)
X_train = knn_imputer.transform(X_train)
X_test = knn_imputer.transform(X_test)'''

# Perform Synthetic Minority Oversampling TEchnique in order to synthetically balance the dataset
# The n of each class is increased to match the n of the largest class
#TODO: Make a little function to sort the n, if it is greater than 600, keep n, if less than smote to 600
over_strategy = {0: 600, 1: 600, 2: 910, 3: 600, 4: 2500, 5: 1180, 6: 600, 7: 600} #Consider that this is the training class, so there is a reduction in n by 10%
oversample = SMOTE(sampling_strategy=over_strategy)
under_strategy = {0: 600, 1: 600, 2: 600, 3: 600, 4: 600, 5: 600, 6: 600, 7: 600}
undersample = RandomUnderSampler(sampling_strategy=under_strategy)

# set up a pipline to perform both transformations
steps = [('o', oversample), ('u', undersample)]
pipeline = Pipeline(steps=steps)
# Perform Synthetic Minority Oversampling TEchnique in order to synthetically balance the dataset
#oversample = SMOTE()
#X_train, y_train = oversample.fit_resample(X_train, y_train)

#oversample the training set
#X_train, y_train = oversample.fit_resample(X_train, y_train)
#Oversmaple the whole set
# X_smote, y_smote = oversample.fit_resample(X, y_enc)
#Use over/under pipeline to create a balanced dataset
X_train, y_train = pipeline.fit_resample(X_train, y_train)

# Make sure that the classes have been balanced
counter2 = Counter(y_train)
for key, value in counter2.items():
    per = value / len(y_train) * 100
    print('Class=%s, n=%d (%.2f%%)' % (key, value, per))

#print(X_train)
#print(y_test.shape)

# Random forest classifier
# n_estimators=100, criterion='entropy', random_state=42
extra_trees = ExtraTreesClassifier(criterion='entropy', max_depth=100, n_estimators=500, random_state=42)
extra_trees.fit(X_train, y_train)

####################################################################################
# Optimization process
###################################################################################
'''
#cross validation for evaluation
cv = RepeatedStratifiedKFold(n_splits=10, n_repeats=3, random_state=1)

#define optimization search space
space = dict()
space['n_estimators'] = [100, 500, 1000]
space['criterion'] = ['gini', 'entropy', 'log_loss']
space['max_depth'] = [80, 90, 100, 110]
space['random_state'] = [None, 41, 117]

#define the search. Took about 1 hour with n_split=5
#Best Score: 0.9413081972877256
#Best Hyperparameters: {'criterion': 'log_loss', 'max_depth': 100, 'n_estimators': 500, 'random_state': None}

search = GridSearchCV(extra_trees, space, scoring='accuracy', n_jobs=-1, cv=cv)

#execute the search
result = search.fit(X_train, y_train)

print('Best Score: %s' % result.best_score_)
print('Best Hyperparameters: %s' % result.best_params_)
'''

##################################################################################
# Train and Test Process
##################################################################################

y_pred = extra_trees.predict(X_test)
# print(y_pred)


#print performance information
print('Overall F1 Score: ' + str(round(f1_score(y_test, y_pred, average='micro'), 3)))
#Convert the y encoding back to string for easy reading
y_test = le.inverse_transform(y_test[:])
y_pred = le.inverse_transform(y_pred[:])
print(confusion_matrix(y_test, y_pred))
print(classification_report(y_test, y_pred))


#################################################################################
# Store the Final Model
#################################################################################
# Store the trained model

filename = r'PGR_Dataset_1\Models\leftleg_Double60_031423.sav'
joblib.dump(extra_trees, filename)
print(filename)

'''
#to load the model and predict later
loaded_model = joblib.load('extratreestrainedmodel.sav')
result = loaded_model.predict(X_data, y_data)
print(result)
'''
