from pymongo import MongoClient


class Database:
    """Abstraction layer for database for this project."""

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
                output.append([name, str(collection.insert(activity))])
            except Exception as err:
                output.append([name, str(err)])

        return output

    def get_activities(self, opts):
        """Get list of Workout Activities from mongo activities collection."""
        db = self.client["workouttracker"]
        collection = db["activities"]
        return collection.find(opts)
