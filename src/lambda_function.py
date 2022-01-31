# Standard Library
import datetime
import json
import os
from pprint import pprint as pp

# Third Party
# Third Party Libraries
from dotenv import load_dotenv
import boto3

# Our Libraries
from database import Database

load_dotenv()
db = Database(os.getenv("MONGO_CONNECTION_STRING"))
s3_client = boto3.client("s3")

BUCKET_NAME = os.getenv("BUCKET_NAME")
KEY_PATH = os.getenv("KEY_PATH")


def lambda_handler(event, context):
    activities = process_activities(list(db.get_activities({"type": {"$in": ["Ride", "VirtualRide"]}})))
    json_data = "\n".join([json.dumps(a) for a in activities])
    s3_client.put_object(Body=json_data, Bucket=BUCKET_NAME, Key=f"{KEY_PATH}/data.json")
    return {"statusCode": 200, "body": json_data}


def process_activities(activities):
    for activity in activities:
        activity["_id"] = str(activity["_id"])
        activity["start_date_local"] = (
            activity["start_date_local"] - datetime.datetime(1970, 1, 1, 0, 0, 0)
        ).total_seconds() * 1000.0
    return activities


if __name__ == "__main__":
    print(lambda_handler({}, {}))
