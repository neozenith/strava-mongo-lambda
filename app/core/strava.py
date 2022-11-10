"""Strava API Wrapper.

Simplify the Strava API with a wrapper to abstract only the tasks needed.
"""

# Standard Library
import time

# Third Party Libraries
import httpx


class StravaAPIWrapper:
    """Simplify the Strava API with a wrapper to abstract only the tasks needed."""

    API_ROOT = "https://www.strava.com/api/v3/"

    def __init__(self, client_id, client_secret, credentials, save_credential_callback):
        """Create StravaAPIWrapper instance with an access token."""
        super().__init__()
        self.client_id = client_id
        self.client_secret = client_secret
        self.credentials = credentials
        self.save_credential_callback = save_credential_callback

    def _refresh_credentials(self):
        response = httpx.post(
            f"{self.API_ROOT}oauth/token",
            data={
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

        api_response = httpx.get(
            f"{self.API_ROOT}athlete/activities",
            headers={"Authorization": f"Bearer {self.credentials['access_token']}"},
            params={"per_page": per_page, "page": page, **kwargs},
        ).json()

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
        return {attr: value for attr, value in activity.items() if attr in target_attributes}
