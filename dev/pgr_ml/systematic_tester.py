import imblearn
from imblearn.over_sampling import SMOTE

import pandas as pd
from numpy import mean, std
from collections import Counter
import matplotlib.pyplot as plt

from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import RepeatedStratifiedKFold
from sklearn.metrics import classification_report, confusion_matrix, f1_score

from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import RandomForestClassifier, ExtraTreesClassifier, AdaBoostClassifier, GradientBoostingClassifier


def load_dataset(path):
    df = pd.read_csv(path)

    #get rid of error frames b/c they do not reflect reality
    df_no_error = df[df.iloc[:, -1] != 'error']
    ########
    ##The following line drops every row (entire row) with a Nan value, is there a better way?
    ########
    df_clean = df_no_error.dropna(how='all')
    #print(df_clean.shape)

    #Remove whitespaces in column names
    df_clean.columns = df_clean.columns.str.strip()
    # Seperate the dependent and independent variables
    y = df_clean.iloc[:, -1]
    X = df_clean.drop(y, axis=1)

    #Numerically encode the target variables
    y = LabelEncoder().fit_transform(y)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.10, random_state=42)

    #over or under sampling can be calibrated with the following
    #strategy = {0: 100, 1: 100, 2: 200, 3: 200, 4: 200, 5: 200}
    #oversample = SMOTE(sampling_strategy=strategy)

    # Perform Synthetic Minority Oversampling TEchnique in order to synthetically balance the dataset
    oversample = SMOTE()
    X_train, y_train = oversample.fit_resample(X_train, y_train)

    # Confirm oversampling effect
    counter = Counter(y_train)
    for key, value in counter.items():
        per = value / len(y_train) * 100
        print('Class=%s, n=%d (%.2f%%)' % (key, value, per))
    return X_train, y_train, X_test, y_test


def test_models(X_trn, y_trn, X_tst, model):
    #k-fold seperates the data into 10 randomly selected groups and automatically splits these into test and train groups
    #this is repeated 3 times and the mean accuracy is reported
    #Note: this is done on data after I already split it 90/10. I did this so that I could confidently use F1 scoring and a classification report later
    cv = RepeatedStratifiedKFold(n_splits=10, n_repeats=3, random_state=117)
    scores = cross_val_score(model, X_trn, y_trn, scoring='accuracy', cv=cv, n_jobs=-1)
    fit = model.fit(X_trn, y_trn)
    predict = model.predict(X_tst)
    return scores, fit, predict


Path = 'C:/Users/trott/PycharmProjects/posetracking/ProcessedVideos/labeled csv files/General Label System and Model/minmax_training_set.csv'
X_train, y_train, X_test, y_test = load_dataset(Path)
print(X_train.shape, y_train.shape, Counter(y_train))

models = {
    #Linear Models
    'Multiclass Log Regression': LogisticRegression(solver='newton-cg', multi_class='multinomial', max_iter=150),
    #Nonlinear Models
    'Decision Tree': DecisionTreeClassifier(),
    'SVM': SVC(kernel='rbf', gamma='auto', C=10),
    'KNN': KNeighborsClassifier(),
    #Ensemble Models
    'Random Forest': RandomForestClassifier(n_estimators=100),
    'Extra Trees': ExtraTreesClassifier(n_estimators=100),
}

# evaluate each model
results = []
names = []
for i in models:
    # evaluate the model and store results
    scores, fit, predict = test_models(X_train, y_train, X_test, models[i])
    results.append(scores)
    names.append(i)
    # summarize performance
    print('k-Fold Cross Validation for %s = Mean Accuracy: %.3f (std: %.3f)' % (i, mean(scores), std(scores)))
    print('Overall F1 Score: ' + str(round(f1_score(y_test, predict, average='micro'), 3)))
    print(classification_report(y_test, predict))

plt.boxplot(results, labels=names, showmeans=True)
plt.show()
