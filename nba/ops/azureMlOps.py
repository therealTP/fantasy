import urllib.request
import requests
import json
import time
import urllib
from azure.storage.blob import (BlockBlobService, ContentSettings)

import nba.ops.csvOps as csv
import nba.ops.mlDataPrep as ml

# import config file
with open('./../config.json') as config_file:
    config = json.load(config_file)["MS_AZURE"]

apiHeaders = {
    "Content-Type": "application/json",
    "Authorization": ("Bearer " + config["RETRAIN_API_KEY"])
}

def getPredictions(arrOfFeatureObjs, statType):

    data = {
        "Inputs": {
            "input1": arrOfFeatureObjs
        },
        "GlobalParameters":  {}
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": ("Bearer " + config["PREDICT_KEYS"][statType])
    }

    body = str.encode(json.dumps(data))

    url = config["PREDICT_URLS"][statType]
    
    # req = urllib.request.Request(url, body, headers)
    
    try:
        # response = urllib.request.urlopen(req)
        req = requests.post(url, headers=headers, data=body)
        result = req.json()
        return result
    except urllib.error.HTTPError as error:
        print("The request failed with status code: " + str(error.code))
        return error

        # Print the headers - they include the requert ID and the timestamp, which are useful for debugging the failure
        # print(error.info())
        # print(json.loads(error.read().decode("utf8", 'ignore')))

def createDictFromRow(row, columnsArr):
    newDict = {}

    for index, column in enumerate(columnsArr):
        newDict[column] = row[index]

    return newDict

def getPredictionsForDate(date, statType):
    # get predictior data from api for date & stattype
    featureArr = ml.getAndPrepFinalData(date, statType, False, 10, True)

    predRes = getPredictions(featureArr, statType)

    try:
        predictions = predRes["Results"]["output1"]
        return predictions

    except Exception as e:
        print("ERROR!", e)
        return False

def pullRetrainDataAndWriteToCsv(retrainDate, statType):
    '''
    Pulls in data for a specific date to retrain 
    '''
    folder = './../local-data/retrain-data/'
    filename = retrainDate + '-nba-' + statType + '-retrain-data.csv'
    location = folder + filename

    print("Pulling retraining data from API...")
    # training = True, # recentGames = 10
    data = ml.getAndPrepFinalData(retrainDate, statType, True, 10)

    print("Data pulled, num rows ", len(data))

    print("Writing retraining data to csv w/ header. File location: ", location)
    try:
        csv.writeToCsv(data, location, header=ml.getColumns())
        return location
    except:
        return False

def postFileToStorage(location, filename, container):
    """
    Location: where the file is located on computer
    Filename: what to call file in storage
    Container: which bucket to post file to in storage
    """
    blob_service = BlockBlobService(account_name=config["STORAGE_ACCOUNT"], account_key=config["STORAGE_ACCOUNT_KEY"])

    print("Uploading the input to blob storage...")
    # blob_service.create_blob_from_path(container, filename, location)
    
    response = blob_service.create_blob_from_path(container, filename, location,
    content_settings=ContentSettings(content_type='text/csv'))

    return response

def printHttpError(httpError):
    print("The request failed with status code: " + str(httpError.code))

    # Print the headers - they include the requert ID and the timestamp, which are useful for debugging the failure
    print(httpError.info())

    print(json.loads(httpError.read()))
    return

def processResults(result):

    results = result["Results"]
    for outputName in results:
        result_blob_location = results[outputName]
        sas_token = result_blob_location["SasBlobToken"]
        base_url = result_blob_location["BaseLocation"]
        relative_url = result_blob_location["RelativeLocation"]

        print("The results for " + outputName + " are available at the following Azure Storage location:")
        print("BaseLocation: " + base_url)
        print("RelativeLocation: " + relative_url)
        print("SasBlobToken: " + sas_token)

    return

def runBesJob(filename, statType, retrainDate):
    storage_container_name = config["RETRAIN_STORAGE_CONTAINTER"]
    connection_string = "DefaultEndpointsProtocol=https;AccountName=" + config["STORAGE_ACCOUNT"] + ";AccountKey=" + config["STORAGE_ACCOUNT_KEY"]
    baseUrl = config["RETRAIN_BASE_URLS"][statType]

    payload =  {
        "Inputs": {
            "retrain-input": { 
                "ConnectionString": connection_string, 
                "RelativeLocation": "/" + storage_container_name + "/" + filename
            },
        },     
        "Outputs": {
            "retrain-output": {
                "ConnectionString": connection_string, 
                "RelativeLocation": "/" + storage_container_name + "/" + retrainDate + "-" + statType + "-retrain-outputresults.ilearner" 
            },
            "eval-output": { 
                "ConnectionString": connection_string, 
                "RelativeLocation": "/" + storage_container_name + "/" + retrainDate + "-" + statType + "-eval-outputresults.csv" 
            }
        },
        "GlobalParameters": {}
    }

    # print("PAYLOAD", payload)

    body = str.encode(json.dumps(payload))
    
    # submit the job
    print("Submitting the job...")

    submitJobUrl = baseUrl + "?api-version=2.0"
    try:
        submitResponse = requests.post(submitJobUrl, headers=apiHeaders, data=body)
    except HTTPError as e:
        printHttpError(e)
        return

    job_id = submitResponse.json()
    # job_id = submitResult[1:-1] # remove the enclosing double-quotes
    print("Job ID: " + job_id)

    # start the job
    print("Starting the job...")
    startJobUrl = baseUrl + "/" + job_id + "/start?api-version=2.0"

    startHeaders = { "Authorization":("Bearer " + config["RETRAIN_API_KEY"]) }

    try:
        startResponse = requests.post(startJobUrl, headers=startHeaders, data=json.dumps({}))
    except HTTPError as e:
        printHttpError(e)
        return
    except Error as e:
        print("OTHER START JOB ERROR", e)
        return

    # check status of job until true
    checkStatusUrl = baseUrl + "/" + job_id + "?api-version=2.0"

    while True:
        print("Checking the job status...")

        try:
            checkResponse = requests.get(checkStatusUrl, headers=startHeaders)
        except HTTPError as e:
            printHttpError(e)
            return
        except Error as e:
            print("OTHER CHECK JOB ERROR", e)
            return

        checkResult = checkResponse.json()
        status = checkResult["StatusCode"]
        if (status == 0 or status == "NotStarted"):
            print("Job " + job_id + " not yet started...")
        elif (status == 1 or status == "Running"):
            print("Job " + job_id + " running...")
        elif (status == 2 or status == "Failed"):
            print("Job " + job_id + " failed!")
            print("Error details: " + result["Details"])
            break
        elif (status == 3 or status == "Cancelled"):
            print("Job " + job_id + " cancelled!")
            break
        elif (status == 4 or status == "Finished"):
            print("Job " + job_id + " finished!")
            processResults(checkResult)
            break
        time.sleep(1) # wait one second
    return

# --- RETRAINING FCNS --- #
def retrainModel(retrainDate, statType):
    # https://docs.microsoft.com/en-us/azure/machine-learning/machine-learning-retrain-models-programmatically
    # https://studio.azureml.net/apihelp/workspaces/d2c4ddfb357d488d890c735fef20fdec/webservices/d97c8e7fcebe44a7a2b4c4c31e5d5f83/endpoints/8252b3048a2e41c5a6b38c8b10b956a4/jobs

    # pull retrain data & write to csv
    # location = pullRetrainDataAndWriteToCsv(retrainDate, statType)

    # new filename to call in azure storage
    filename = retrainDate + '-nba-' + statType + '-retrain-data.csv'
    container = config["RETRAIN_STORAGE_CONTAINTER"]

    # post retrain CSV to azure storage
    # postFileToStorage(location, filename, container)

    # run BES jub
    runBesJob(filename, statType, retrainDate)

    # look up model for stat type
    # modelUrl = 

    # post BES job pointing to CSV & model (don't start)
    # returns: job ID

    # start BES job w/ job id

    # check status of job until complete
    # jobFinished = False
    # while jobFinished is False:
        # check status of job
        # if finished:
        ## save data
        ## break out
        # else:
        ## wait 5 seconds

    # after complete, update trained model

    # delete job

