from backend.core.model.auth import GoogleAuthRequest, GoogleUserInfo
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

class GoogleAuthProvider:
    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret

    async def verify_token(self, token: str) -> GoogleUserInfo:
        try:
            id_info = id_token.verify_oauth2_token(token, google_requests.Request(), self.client_id)
            return GoogleUserInfo(**id_info)
        except Exception as e:
            raise e