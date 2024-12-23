from fastapi_users.authentication import CookieTransport, AuthenticationBackend, JWTStrategy
from config import SECRET_JWT

cookie_transport = CookieTransport(cookie_name="bonds", cookie_max_age=3600, cookie_secure=False, cookie_httponly=True, cookie_path="/",)

SECRET = SECRET_JWT

def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=SECRET, lifetime_seconds=3600)

auth_backend = AuthenticationBackend(
    name="jwt",
    transport=cookie_transport,
    get_strategy=get_jwt_strategy,
)
