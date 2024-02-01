# Standard Library
import os
from pprint import pprint as pp
from functools import wraps


# Third Party Libraries
import boto3
from dotenv import load_dotenv
from fastapi import FastAPI, Request, Response
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from mangum import Mangum

from .core import extract, load, sync
from .core.auth import (
    authenticate_request,
    handle_auth_redirect,
    handle_logout,
    redirect_to_login
)

from .core.cognito import CognitoWrapperFactory

cognito = CognitoWrapperFactory()


##################### BEGIN LAMBDA COLD START CODE #####################

# instead of re-downloading the public keys every time
# we download them only on cold start
# https://aws.amazon.com/blogs/compute/container-reuse-in-lambda/
JWKS = cognito.get_jwks()

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


#TODO: https://stackoverflow.com/a/72644609/622276
#TODO: https://stackoverflow.com/a/64656733/622276
#TODO: https://stackoverflow.com/a/75908754/622276
#TODO: https://fastapi.tiangolo.com/tutorial/dependencies/dependencies-in-path-operation-decorators/#add-dependencies-to-the-path-operation-decorator
#TODO: https://fastapi.tiangolo.com/tutorial/middleware/
#TODO: https://fastapi.tiangolo.com/advanced/middleware/
# credentials_exception = HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED,
#         detail="Could not validate credentials",
#         headers={"WWW-Authenticate": "Bearer"},
#     )


def auth_required(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        return await func(*args, **kwargs)

    return wrapper

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/extract")
@auth_required
async def extract_activities(request: Request, response: Response, after_days_ago: int = 1):
    """Extract activities from Strava into Mongo."""
    authenticated_claims = await authenticate_request(request, JWKS)
    if not authenticated_claims:
        return redirect_to_login(request)
    elif not authenticated_claims["id"] or not authenticated_claims["access"]:
        token = await cognito.exchange_auth2_refresh_token(refresh_token = request.cookies.get("refresh_token", None))
        return handle_auth_redirect(request, response, token)

    return extract(after_days_ago=after_days_ago)


@app.get("/load")
@auth_required
async def load_activities(request: Request, response: Response):
    """Load activities from Mongo into GSheet."""
    authenticated_claims = await authenticate_request(request, JWKS)
    if not authenticated_claims:
        return redirect_to_login(request)
    elif not authenticated_claims["id"] or not authenticated_claims["access"]:
        token = await cognito.exchange_auth2_refresh_token(refresh_token = request.cookies.get("refresh_token", None))
        return handle_auth_redirect(request, response, token)
    
    load()
    return {"status": "success"}


@app.get("/sync")
@auth_required
async def sync_activities(request: Request, response: Response, after_days_ago: int = 1):
    """Extract and Load activities from Strava to GSheet."""
    authenticated_claims = await authenticate_request(request, JWKS)
    if not authenticated_claims:
        return redirect_to_login(request)
    elif not authenticated_claims["id"] or not authenticated_claims["access"]:
        token = await cognito.exchange_auth2_refresh_token(refresh_token = request.cookies.get("refresh_token", None))
        return handle_auth_redirect(request, response, token)

    return sync(after_days_ago=after_days_ago)


@app.get("/auth")
async def get_auth(request: Request, response: Response, code: str = None):
    if code:
        token = await cognito.exchange_oauth2_code(code)
        return handle_auth_redirect(request, response, token)
    else:
        return response


@app.get("/logout")
async def logout(request: Request, response: Response, code: str = None):
    return handle_logout(response)


handler = Mangum(app)
