import boto3
import json

def putObjectS3(data_object, bucket, bucket_location=""):
    """
    data object is file of json to put
    bucket_location is optional folder name in bucket
    """
    try:
        # create s3 object
        s3 = boto3.resource('s3')

        # open data object to post
        data = open(data_object, 'rb')

        # create object key based on bucket location & data object name
        object_key = bucket_location + data_object

        # put object into bucket
        s3.Bucket(bucket).put_object(Key=object_key, Body=data)

        # return true for success
        return True

    except:
        # return false for failure
        return False

def getObjectS3(bucket, key):
    """
    get s3 json object
    return python dict
    """
    try:
        # create s3 object
        s3 = boto3.resource('s3')

        # get object, decode, convert to python dict
        dataObj = json.loads(s3.Object(bucket, key).get()['Body'].read().decode('utf-8'))

        return dataObj

    except:
        # return false for failure
        return False
