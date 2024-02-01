# Standard Library
from functools import cache
import base64
import os
import time

# Third Party Libraries
import httpx
from dotenv import load_dotenv


load_dotenv()

COGNITO_HOST = os.getenv("COGNITO_HOST")
AWS_REGION = os.getenv("AWS_REGION")
COGNITO_CLIENT_ID = os.getenv("COGNITO_CLIENT_ID")
COGNITO_CLIENT_SECRET = os.getenv("COGNITO_CLIENT_SECRET")
COGNITO_USERPOOL_ID = os.getenv("COGNITO_USERPOOL_ID")
COGNITO_REDIRECT_URI = os.getenv("COGNITO_REDIRECT_URI")

DEFAULT_SCOPES = ["email", "aws.cognito.signin.user.admin", "openid"]


class CognitoWrapper:
    """Simplify the Cognito API with a wrapper to abstract only the tasks needed."""

    def __init__(self, host, client_id, client_secret, user_pool_id, redirect_uri, scopes = DEFAULT_SCOPES, region = AWS_REGION):
        """Configure GoogleSheet client for a target worksheet."""
        super().__init__()
        self.host = host
        self.client_id = client_id
        self.client_secret = client_secret
        self.user_pool_id = user_pool_id
        self.redirect_uri = redirect_uri
        self.scopes = scopes
        self.region  = region


    def get_jwks(self, jwk_keys_url = None):
        """Get keys from JSON payload of JWKs URL."""
        url = jwk_keys_url if jwk_keys_url else self.get_jwks_url()
        with httpx.Client() as client:
            result = client.get(url).json()

        return result["keys"]

    @cache
    def get_jwks_url(self):
        return f"https://cognito-idp.{self.region}.amazonaws.com/{self.user_pool_id}/.well-known/jwks.json"


    def get_login_uri(self):
        
        parameters = {
            "client_id": self.client_id,
            "response_type": "code",
            "scope": "+".join(self.scopes),
            "redirect_uri": self.redirect_uri,
        }
        query_params = "&".join([f"{k}={v}" for k, v in parameters.items()])
        LOGIN_URI = f"{self.host}/login?{query_params}"
        return LOGIN_URI

    async def exchange_oauth2_code(self, code):
        """Exchange authorization code for OAuth2 token.

        https://docs.aws.amazon.com/cognito/latest/developerguide/token-endpoint.html
        """
        token = None
        URI = f"{self.host}/oauth2/token"
        basic_auth = base64.b64encode(f"{self.client_id}:{self.client_secret}".encode("ascii")).decode()
        headers = {"Authorization": f"Basic {basic_auth}", "Content-Type": "application/x-www-form-urlencoded"}
        data = {
            "grant_type": "authorization_code",
            "client_id": self.client_id,
            "code": code,
            "redirect_uri": self.redirect_uri,
        }
        async with httpx.AsyncClient() as client:
            token = await client.post(URI, headers=headers, data=data)
            token = token.json()
        return token
    
    async def exchange_auth2_refresh_token(self, refresh_token):
        """Exchange refresh token for OAuth2 token.

        https://docs.aws.amazon.com/cognito/latest/developerguide/amazon-cognito-user-pools-using-the-refresh-token.html
        """
        token = None
        URI = f"{self.host}/oauth2/token"
        basic_auth = base64.b64encode(f"{self.client_id}:{self.client_secret}".encode("ascii")).decode()
        headers = {"Authorization": f"Basic {basic_auth}", "Content-Type": "application/x-www-form-urlencoded"}
        data = {
            "grant_type": "refresh_token",
            "client_id": self.client_id,
            "refresh_token": refresh_token,
            "redirect_uri": self.redirect_uri,
        }
        async with httpx.AsyncClient() as client:
            token = await client.post(URI, headers=headers, data=data)
            token = token.json()
        return token

@cache
def CognitoWrapperFactory():
    return CognitoWrapper(
        host=COGNITO_HOST,
        client_id=COGNITO_CLIENT_ID,
        client_secret=COGNITO_CLIENT_SECRET,
        user_pool_id=COGNITO_USERPOOL_ID,
        redirect_uri=COGNITO_REDIRECT_URI,
        scopes=DEFAULT_SCOPES,
        region=AWS_REGION
    )