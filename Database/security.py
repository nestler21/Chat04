from connexion.exceptions import OAuthProblem
from hashlib import sha256
from connexion.exceptions import OAuthProblem


def verify_apikey(token, required_scopes):
    APIKEY_HASH = "6641020d80e10877a13a973592d934165de39c743f7a2fa3f78a8671ac2e9c5b"
    token_hash = sha256(token.encode('utf-8')).hexdigest()
    if token_hash != APIKEY_HASH:
        raise OAuthProblem("Invalid ApiKey")
    return {'sub': token_hash}