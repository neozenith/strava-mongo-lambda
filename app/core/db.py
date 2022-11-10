"""Database Wrapper.

This project uses MongoDB but the specific tasks should
be abstracted and independent of the underlying technology.
"""
# Third Party Libraries
from pymongo import MongoClient


class Database:
    """Abstraction layer for database used in this project."""

    def __init__(self, connection_string):
        """Initialize Database client with a connection string."""
        super().__init__()
        self.client = MongoClient(connection_string)

    def save_activities(self, activities):
        """Save list of Strava Activities to mongo activities collection."""
        db = self.client["workouttracker"]
        collection = db["activities"]
        output = []
        for activity in activities:
            name = activity["name"]
            try:
                output.append([name, str(collection.insert_one(activity).inserted_id)])
            except Exception as err:
                output.append([name, str(err)])

        return output

    def get_activities(self, opts):
        """Get list of Workout Activities from mongo activities collection."""
        db = self.client["workouttracker"]
        collection = db["activities"]
        return collection.find(opts)

    def get_user(self, username):
        """Get User from mongo users collection."""
        db = self.client["workouttracker"]
        collection = db["users"]
        return collection.find_one({"username": username})

    def get_credential(self, credential_id):
        """Get Credential from mongo credentials collection."""
        db = self.client["workouttracker"]
        collection = db["credentials"]
        result = collection.find_one({"id": credential_id})

        return result["value"]

    def save_credentials(self, credential_id, credentials):
        """Save Credential to mongo credentials collection."""
        db = self.client["workouttracker"]
        collection = db["credentials"]
        document = collection.find_one({"id": credential_id})

        document["value"] = credentials

        collection.update_one({"_id": document["_id"]}, {"$set": document}, upsert=False)
