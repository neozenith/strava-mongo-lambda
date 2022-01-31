# strava-mongo-lambda

Creating a lambda to extract my strava data from a mongodb instance

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
