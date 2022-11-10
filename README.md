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