import json
import os

# Our Libraries
from database import Database

# Third Party Libraries
from dotenv import load_dotenv

load_dotenv()
db = Database(os.getenv("MONGO_CONNECTION_STRING"))


def lambda_handler(event, context):
    activities = list(db.get_activities({"type": {"$in": ["Ride", "VirtualRide"]}}))
    return {"statusCode": 200, "body": json.dumps(activities)}
