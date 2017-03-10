# AUTH TO GCLOUD THROUGH SDK: https://googlecloudplatform.github.io/google-cloud-python/stable/google-cloud-auth.html
# BETA Python3 Google App Engine: https://cloudplatform.googleblog.com/2016/08/python-3-on-Google-App-Engine-flexible-environment-now-in-beta.html
# Manage SDK Components via CLI
# Supported cloud services: https://developers.google.com/api-client-library/python/apis/?authuser=1
# Prediction dev guide: https://cloud.google.com/prediction/docs/developer-guide
# Prediction API Python Ref: https://developers.google.com/resources/api-libraries/documentation/prediction/v1.6/python/latest/prediction_v1.6.trainedmodels.html#get
import logging
import os
import json
import pprint
import nba.ops.mlDataPrep as ml
import time

from gcloud import storage
from apiclient.discovery import build

with open('./../config.json') as config_file:
    config = json.load(config_file)["GOOGLE_CLOUD"]

def uploadCsvToGoogleStorage(filename, location):
    client = storage.Client(config["PROJECT_ID"])
    bucket = client.get_bucket(config["STORAGE_BUCKET"])
    blob = bucket.blob(filename)

    with open(location, 'rb') as csv_file:
        blob.upload_from_file(csv_file)

    # return location of file: bucket + filename
    return config["STORAGE_BUCKET"] + "/" + filename

def createAndTrainNewModel(statType, trainDataLocation):
    service = build('prediction', 'v1.6')
    trainer = service.trainedmodels()

    modelId = config["MODEL_IDS"][statType]
    modelType = 'REGRESSION'

    trainBody = {
        "id": modelId,
        "storageDataLocation": trainDataLocation,
        "modelType": modelType 
    }

    return trainer.insert(project=config["PROJECT_ID"], body=trainBody).execute()

def createAndTrainNewModelWithDateRange(dateRange, statType):
    trainingDataLoc = ml.pullGoogleTrainingDataAndWriteToCsv(dateRange, statType)
    filename = 'nba-' + statType + '-google-initial-training-data.csv'
    # uploadLocation = config["STORAGE_BUCKET"] + "/" + filename # TEST
    uploadLocation = uploadCsvToGoogleStorage(filename, trainingDataLoc)
    createModelResponse = createAndTrainNewModel(statType, uploadLocation)
    return createModelResponse

def listPredictionModels():
    service = build('prediction', 'v1.6')
    trainer = service.trainedmodels()

    return trainer.list(project=config["PROJECT_ID"]).execute()

def analyzePredictionModel(statType):
    service = build('prediction', 'v1.6')
    trainer = service.trainedmodels()
    modelId = config["MODEL_IDS"][statType]
    return trainer.analyze(project=config["PROJECT_ID"], id=modelId).execute()

def getTrainingStatusOfModel(statType):
    service = build('prediction', 'v1.6')
    trainer = service.trainedmodels()
    modelId = config["MODEL_IDS"][statType]
    return trainer.get(project=config["PROJECT_ID"], id=modelId).execute()

def getPrediction(statType, featureArr):
    service = build('prediction', 'v1.6')
    predictor = service.trainedmodels()

    modelId = config["MODEL_IDS"][statType]

    body = {
        'input': {
            'csvInstance': featureArr
        }
    }

    try:
        predictionResponse = predictor.predict(project=config["PROJECT_ID"], id=modelId, body=body).execute()
        return max(float(predictionResponse["outputValue"]), float(0)) # prevent negative vals
    except Exception as e:
        if e.__class__.__name__ == 'googleapiclient.errors.HttpError':
            print("CAUGHT HTTP ERR GOOGLE")
            time.sleep(105)
            predictionResponse = predictor.predict(project=config["PROJECT_ID"], id=modelId, body=body).execute()
            return max(float(predictionResponse["outputValue"]), float(0)) # prevent negative vals
        else:
            raise ValueError("Error getting prediction")

def getPredictionsForDate(date, statType):
    predictData = ml.getAndPrepFinalData(date, statType, False, 10)

    predictionsForDate = []

    print("Pulling predictions for", date)

    for row in predictData:
        rowObj = {}

        # get bref id for row
        if statType == 'tpt':
            rowObj["bref_id"] = row[3]
        else:
            rowObj["bref_id"] = row[4]

        rowObj["Scored Label"] = getPrediction(statType, row)

        predictionsForDate.append(rowObj)
    
    return predictionsForDate

def deletePredictionModel(statType):
    service = build('prediction', 'v1.6')
    deleter = service.trainedmodels()

    modelId = config["MODEL_IDS"][statType]
    
    return deleter.delete(project=config["PROJECT_ID"], id=modelId).execute()

def retrainModel(statType, retrainRows):
    service = build('prediction', 'v1.6')
    retrainer = service.trainedmodels()
    modelId = config["MODEL_IDS"][statType]

    for row in retrainRows:
        body = {
            "output": float(row[0]), # The generic output value - could be regression value or class label
            "csvInstance": row[1:]
        }

        retrainer.update(project=config["PROJECT_ID"], id=modelId, body=body).execute()

    return "DONE RETRAINING"

def retrainModelWithDate(gameDate, statType):
    retrainRows = ml.getAndPrepFinalData(gameDate, statType, True, 10)
    return retrainModel(statType, retrainRows)

def waitForModelToRetrain(statType):
    while True:
        trainingStatusRes = getTrainingStatusOfModel(statType)
        status = trainingStatusRes["trainingStatus"]

        if status == 'DONE':
            return 'DONE'
        else:
            print("Model still training w/ status", status)
            time.sleep(5)
            continue
    



