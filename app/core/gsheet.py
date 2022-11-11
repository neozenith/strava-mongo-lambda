"""Google Sheet API Wrapper.

Simplify the Google Sheet API with a wrapper to abstract only the tasks needed.
"""
# Standard Library
import datetime

# Third Party Libraries
import gspread
from gspread.utils import ServiceAccountCredentials


class GoogleSheetWrapper:
    """Simplify the Google Sheet API with a wrapper to abstract only the tasks needed."""

    def __init__(self, credentials, sheet_id, worksheet_name):
        """Configure GoogleSheet client for a target worksheet."""
        super().__init__()
        self.credentials = credentials
        self.sheet_id = sheet_id
        self.worksheet_name = worksheet_name

        credentials = ServiceAccountCredentials.from_service_account_info(
            self.credentials,
            scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"],
        )

        self.gclient = gspread.authorize(credentials)
        self.sheet = self.gclient.open_by_key(self.sheet_id)
        self.worksheet = self.sheet.worksheet(self.worksheet_name)

    def save_activities(self, activities):
        """Save an array of Strava SummaryActivity dictionaries to a target worksheet."""
        row_count = len(activities)
        col_names = [k for k in activities[0].keys() if k != "_id"]
        header_names = [" ".join(k.split("_")) for k in col_names]
        col_count = len(col_names)

        header_rangeref = f"A1:{chr(64+col_count)}1"
        self.worksheet.update(header_rangeref, [header_names])

        record_rangref = f"A2:{chr(64+col_count)}{row_count+2}"
        # Zero out old values
        self.worksheet.update(record_rangref, [["" for c in col_names] for row in activities])

        serialized_output = [[self._serialize(c, row.get(c, "")) for c in col_names] for row in activities]

        self.worksheet.update(record_rangref, serialized_output)

    def _serialize(self, key, value):
        if key == "start_date_local":
            # Convert to Google Sheets datetime number format
            # starting from 1899/12/30 00:00:00 as float(0) days
            # return (value - datetime.datetime(1899, 12, 30, 0, 0, 0)).total_seconds() / 86400.0
            if type(value) == str:
                value = datetime.datetime.strptime(value, "%Y-%m-%dT%H:%M:%S%z").replace(tzinfo=None)
            
            return (value - datetime.datetime(1970, 1, 1, 0, 0, 0)).total_seconds() * 1000.0

        elif key in ["average_speed", "max_speed"]:
            # Convert miles to kilometres
            return value * 1.60934
        else:
            return value
