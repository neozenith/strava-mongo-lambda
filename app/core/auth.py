import time

# Third Party Libraries
import httpx
from fastapi import Request, Response
from fastapi.responses import RedirectResponse
from jose import jwk, jwt
from jose.utils import base64url_decode

from .cognito import CognitoWrapperFactory

cognito = CognitoWrapperFactory()


async def authenticate_request(request, JWKS, claimed_audience = cognito.client_id):
    # print(f"authenticate_request#0 {request.url=}")

    id_token = request.cookies.get("id_token", None)
    access_token = request.cookies.get("access_token", None)
    refresh_token = request.cookies.get("refresh_token", None)

    print(f"authenticate_request#1 {id_token=}")
    if not id_token:
        return False

    id_authenticated_claims = authenticated_jwt(token=id_token, jwk_keys=JWKS, claimed_audience=claimed_audience)
    access_authenticated_claims = authenticated_jwt(token=access_token, jwk_keys=JWKS, claims_key="client_id", claimed_audience=claimed_audience)

    # TODO: if authenticated claims return false then trigger refresh token flow.
    print(f"authenticate_request#3 {id_authenticated_claims=}")
    print(f"authenticate_request#3 {access_authenticated_claims=}")

    return {"id": id_authenticated_claims, "access": access_authenticated_claims}


def redirect_to_login(request):
    """Return a Response to Redirect to Login URI."""
    response = RedirectResponse(cognito.get_login_uri())
    # Only set a new redirect post login if it is not already set
    if not request.cookies.get("redirect_post_login", None):
        response.set_cookie(key="redirect_post_login", value=request.url)
    return response


def handle_auth_redirect(request: Request, response: Response, token: str):
    """Redirect to original request if a token is provided.

    Also set the tokens as a cookie
    """
    if not token:
        return response

    referer_url = request.cookies.get("redirect_post_login", "/")
    referer_url = referer_url if referer_url else "/"

    response.status_code = 307
    response.headers["location"] = referer_url
    response.delete_cookie(key="redirect_post_login")
    response.set_cookie(key="id_token", value=token["id_token"], secure=True, httponly=True)
    response.set_cookie(key="access_token", value=token["access_token"], secure=True, httponly=True)
    response.set_cookie(key="refresh_token", value=token["refresh_token"], secure=True, httponly=True)

    return response


def handle_logout(response: Request):
    response.delete_cookie(key="id_token")
    response.delete_cookie(key="access_token")
    response.delete_cookie(key="refresh_token")
    response.delete_cookie(key="redirect_post_login")
    response.status_code = 307
    response.headers["location"] = "/"
    return response

def authenticated_jwt(token, jwk_keys, claimed_audience, claims_key="aud"):
    if not token:
        return False

    headers = jwt.get_unverified_headers(token)

    # search for the kid in the downloaded public keys
    K = [k for k in jwk_keys if k["kid"] == headers["kid"]]
    if not K:  # If empty list of matches
        print("Public key not found in jwks.json")
        return False

    public_key = jwk.construct(K[0])
    message, encoded_signature = str(token).rsplit(".", 1)
    decoded_signature = base64url_decode(encoded_signature.encode("utf-8"))

    # verify the signature
    if not public_key.verify(message.encode("utf8"), decoded_signature):
        print("Signature verification failed")
        return False

    print("Signature successfully verified")

    claims = jwt.get_unverified_claims(token)

    if time.time() > claims["exp"]:
        print("Token is expired")
        return False

    if claims_key in claims and claims[claims_key] != claimed_audience:
        print("Token was not issued for this audience")
        return False
    
    print("Token and Claims successfully verified")

    return claims