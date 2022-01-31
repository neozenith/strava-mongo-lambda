# strava-mongo-lambda

Creating a lambda to extract my strava data from a mongodb instance.

In particular, I like to engage in virtual cycling on the [Zwift](https://zwift.com) platform. Which then saves my indoor cycling activities to [Strava](https://strava.com) as `VirtualRide` activities.

Then [strava-gsheet-python](https://github.com/neozenith/strava-gsheet-python) is a Heroku project I use to extract my ride data to a free tier [Mongo Atlas](https://www.mongodb.com/atlas/database) database on it's way to a Google Sheet where I perform analysis.

So the MongoDB instance deduplicates the entries and is a source of truth.

This Lambda reads from MongoDB and saves the results to S3 where I am planning on migrating to Athena and QuickSight.

## Getting started

```sh
python3 tasks.py init
. ./.venv/bin/activate

inv --list
Available tasks:

  build    Build the lambda into the dist folder.
  deploy   Package lambda and dependencies into a zip, upload to S3 and update target function code.
  format   Autoformat code and sort imports.
  lint     Run linting and formatting checks.
  test     Run pytest.
```
