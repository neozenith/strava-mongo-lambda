# strava-mongo-lambda

In particular, I like to engage in virtual cycling on the [Zwift](https://zwift.com) platform. Which then saves my indoor cycling activities to [Strava](https://strava.com) as `VirtualRide` activities.

This project exposes a FastAPI tiny webserver API behind an AWS lambda funtion URL which is protected with OAuth2 via Cognito.

The API allows me to securely trigger a sync of my Strava data to a Google Sheet for further analysis.

As an intermediate, this sync will save a copy of the Strava activities to a free tier of Mongo Atlas, giving me the option to pivot away from Google Sheets later.

# Local Development

```sh
invoke dev
```

# Deployment

## Setup

You will need to define credential details in `.env` and also log into ECR registry.
You will also need Docker installed and active to build lambda container image

```sh
invoke ecr-login
```

## Build Artifact 

```sh
invoke build-lambda-container deploy-lambda-container
```

## Go Live

This part is still clickops to make the lambda point at the latest uploaded image.
Room for automation improvement of course.

# Maintenance

## Strava SDK

<details>
<summary><b>[OPTIONAL] Generate Strava SDK using Swagger Codegen</b></summary>

### Step 1 - Generate SDK

```bash
# Using OAPIv3 codegen
brew install swagger-codegen
swagger-codegen generate -i https://developers.strava.com/swagger/swagger.json -l python -o strava
```

This will create:
```sh
strava
├── README.md
├── docs
│   ├── ActivitiesApi.md
│   ├── ...
│   └── Zones.md
├── git_push.sh
├── requirements.txt
├── setup.py
├── swagger_client
│   ├── __init__.py
│   ├── api
│   │   ├── __init__.py
│   │   ├── activities_api.py
│   │   ├── .....
│   │   └── uploads_api.py
│   ├── api_client.py
│   ├── configuration.py
│   ├── models
│   │   ├── __init__.py
│   │   ├── activities_body.py
│   │   ├── ...
│   │   └── zones.py
│   └── rest.py
├── test
│   ├── __init__.py
│   ├── test_activities_api.py
│   ├── ...
│   └── test_zones.py
├── test-requirements.txt
└── tox.ini
```

### Step 2 - Update `app/core/strava.py`

For what I needed I decided that using the swagger generated code was overkill.

`app/core/strava.py` is a `httpx` implementation of the raw API for just the requests I needed.

In particular I only needed the `/athlete/activities` endpoint.

So just check the filtered attributes that are grabbed are still the subset we want and there are no typos, renames, missing attributes or new attributes we wish to include.

</details>
