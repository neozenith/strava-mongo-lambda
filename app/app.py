# Standard Library
import os

# Third Party Libraries
import boto3
from dotenv import load_dotenv
from fastapi import FastAPI, Request, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from mangum import Mangum

from .core import extract, load, sync
from .core.auth import (
    authenticate_request,
    handle_auth_redirect,
    handle_logout,
    redirect_to_login,
)
from .core.cognito import (
    AWS_REGION,
    COGNITO_USERPOOL_ID,
    exchange_oauth2_code,
    get_jwks,
)

load_dotenv()

##################### BEGIN LAMBDA COLD START CODE #####################

# instead of re-downloading the public keys every time
# we download them only on cold start
# https://aws.amazon.com/blogs/compute/container-reuse-in-lambda/
JWKS = get_jwks(userpool_id=COGNITO_USERPOOL_ID, region=AWS_REGION)
# for k in JWKS:
#     print(k)

boto3_session = None
if os.getenv("AWS_PROFILE", None) is not None:
    # Local dev uses profile by name
    boto3_session = boto3.Session(profile_name=os.getenv("AWS_PROFILE"), region_name=os.getenv("AWS_REGION"))
else:
    # Deployed lambda uses injected variables
    boto3_session = boto3.Session(
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        aws_session_token=os.getenv("AWS_SESSION_TOKEN"),
        region_name=os.getenv("AWS_REGION"),
    )

##################### END LAMBDA COLD START CODE #####################

app = FastAPI()
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")


@app.get("/")
async def root(request: Request):
    return {"message": "Hello"}


@app.get("/extract")
async def extract_activities(request: Request, after_days_ago: int = 1):
    """Extract activities from Strava into Mongo."""
    authenticated_claims = authenticate_request(request, JWKS)
    if not authenticated_claims:
        return redirect_to_login(request)

    return len(extract(after_days_ago=after_days_ago))


@app.get("/load")
async def load_activities(request: Request):
    """Load activities from Mongo into GSheet."""
    authenticated_claims = authenticate_request(request, JWKS)
    if not authenticated_claims:
        return redirect_to_login(request)

    load()
    return {"status": "success"}


@app.get("/sync")
async def sync_activities(request: Request, after_days_ago: int = 1):
    """Extract and Load activities from Strava to GSheet."""
    authenticated_claims = authenticate_request(request, JWKS)
    if not authenticated_claims:
        return redirect_to_login(request)

    return sync(after_days_ago=after_days_ago)


@app.get("/auth")
async def get_auth(request: Request, response: Response, code: str = None):
    if code:
        token = await exchange_oauth2_code(code)
        return handle_auth_redirect(request, response, token)
    else:
        return response


@app.get("/logout")
async def logout(request: Request, response: Response, code: str = None):
    return handle_logout(response)


handler = Mangum(app)
