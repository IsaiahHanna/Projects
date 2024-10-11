'''
Written By Isaiah Hanna 2024-10-05

Purpose: Get recommendation data and train/create KNN model
'''
import os
import sys
import pandas as pd
import numpy as np
import warnings
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score,precision_score,recall_score
from sklearn.preprocessing import StandardScaler
directory_path = os.path.abspath("C:\\Users\\isaia\\AnimeRecommendation")
sys.path.append(directory_path)
from ImportData.DataImport import RecommendationData
from PredictionCreation.FeatureEncoding import FeatureEncoding
os.chdir("C:\\Users\\isaia\\AnimeRecommendation")

def model(animeDf,rewriteRecs: bool = False):
    os.chdir("C:\\Users\\isaia\\AnimeRecommendation\\ImportData")
    if rewriteRecs:
        recExist = RecommendationData(0.8)
        if not recExist:
            print("Recommendation failed, exiting program.")
            exit()
    trainingData = pd.read_csv("recommendationsAltered.csv")
    #Do another check to make sure that no movies/music/OVA are in dataset
    
    for col in animeDf.columns.tolist():
        if animeDf[col].isna().values.any() == True:
            animeDf = animeDf.dropna(subset = [col])
    
    features = FeatureEncoding(animeDf)
    trainingData = pd.merge(trainingData,features,on='uid')
    x = trainingData.drop(['recId','recommendations'],axis = 1)
    y = trainingData['recId']
    xTrain,xTest,yTrain,yTest = train_test_split(x,y,test_size = 0.2)


    #May need to scale the features. If so, do so here.
    scaler = StandardScaler()
    xTrain = scaler.fit_transform(xTrain)
    xTest = scaler.transform(xTest)
    x = scaler.transform(x)

    #Fit model
    knn = KNeighborsClassifier(n_neighbors = 3)
    knn.fit(xTrain,yTrain)
    yPred = knn.predict(xTest)
    accuracy = accuracy_score(yTest, yPred)

    #Uncomment line below to check accuracy
    print("Training Accuracy:", accuracy) 

    #Cross validate and try various values of k
    kValues = [i for i in range (1,31)]
    scores = []

    scaler = StandardScaler()
    x2 = scaler.fit_transform(x)

    with warnings.catch_warnings(action = 'ignore'):
        for k in kValues:
            knn = KNeighborsClassifier(n_neighbors=k)
            score = cross_val_score(knn, x2, y,cv = 2)
            scores.append(np.mean(score))

    knn = KNeighborsClassifier(n_neighbors = kValues[np.argmax(scores)])
    knn.fit(x,y)

    yPredCV = knn.predict(xTest)
    accuracy = accuracy_score(yTest, yPredCV)

    #Uncomment line below to check accuracy
    print("Accuracy:", accuracy)


    return knn,scaler,features

def prediction(df,features,userAnime,numRows):
    knn,scaler,features = model(df)
    if not knn:
        print("KNN model failed to be instantiated. Exiting...")
        exit()
    elif userAnime.empty:
        print("User's input failed to be read. Exiting...")
        exit()
    
    
    #Find nearest neighbors of user's input
    userAnime = userAnime[features.columns.tolist()]
    userScaled = scaler.fit_transform(userAnime)
    neighborsDist,neighborsInd = knn.kneighbors(userScaled,n_neighbors = 5)  #Returns the distance and indices of the nearest neighbors (default is based on the k used in model's constructor)
    
    neighbors = df.iloc[list(neighborsInd)[0]]
    return neighbors
    