"""Strava API Wrapper.

Simplify the Strava API with a wrapper to abstract only the tasks needed.
"""

# Standard Library
import time

# Third Party Libraries
import requests
import swagger_client
from swagger_client.rest import ApiException


class StravaAPIWrapper:
    """Simplify the Strava API with a wrapper to abstract only the tasks needed."""

    def __init__(self, client_id, client_secret, credentials, save_credential_callback):
        """Create StravaAPIWrapper instance with an access token."""
        super().__init__()
        self.client_id = client_id
        self.client_secret = client_secret
        self.credentials = credentials
        self.save_credential_callback = save_credential_callback

    def _refresh_credentials(self):
        response = requests.post(
            "https://www.strava.com/api/v3/oauth/token",
            {
                "grant_type": "refresh_token",
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "refresh_token": self.credentials["refresh_token"],
            },
        )
        self.credentials = response.json()

        self.save_credential_callback("strava", self.credentials)

    def list_activities(self, page=1, per_page=30, **kwargs):
        """Extract a list of athlete activities from Strava API."""
        if self.credentials["expires_at"] <= time.time():
            self._refresh_credentials()

        api_response = []

        try:
            api_instance = swagger_client.ActivitiesApi()
            api_instance.api_client.configuration.access_token = self.credentials["access_token"]
            api_response = api_instance.get_logged_in_athlete_activities(page=page, per_page=per_page, **kwargs)
        except ApiException as e:
            print("Exception when calling ActivitiesApi->getLoggedInAthleteActivities: %s\n" % e)

        return [self._filtered_activity(a) for a in api_response]

    def _filtered_activity(self, activity):
        target_attributes = [
            "id",
            "name",
            "start_date_local",
            "moving_time",
            "elapsed_time",
            "type",
            "workout_type",
            "distance",
            "total_elevation_gain",
            "kilojoules",
            "average_speed",
            "max_speed",
            "average_watts",
            "max_watts",
            "weighted_average_watts",
        ]
        return {attr: getattr(activity, attr) for attr in activity.__dir__() if attr in target_attributes}
