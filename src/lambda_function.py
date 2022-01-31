# Standard Library
import datetime
import json
import os
from pprint import pprint as pp

# Third Party
# Third Party Libraries
from dotenv import load_dotenv

# Our Libraries
from database import Database

load_dotenv()
db = Database(os.getenv("MONGO_CONNECTION_STRING"))


def lambda_handler(event, context):
    activities = list(db.get_activities({"type": {"$in": ["Ride", "VirtualRide"]}}))

    return {"statusCode": 200, "body": json.dumps(process_activities(activities))}


def process_activities(activities):
    for activity in activities:
        activity["_id"] = str(activity["_id"])
        activity["start_date_local"] = (
            activity["start_date_local"] - datetime.datetime(1970, 1, 1, 0, 0, 0)
        ).total_seconds() * 1000.0
    return activities


if __name__ == "__main__":
    print(lambda_handler({}, {}))
