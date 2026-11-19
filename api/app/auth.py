"""Optional shared login (HTTP Basic) for running without nginx. Off unless SHOTOKAN_AUTH is set."""
import base64, hashlib, hmac
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from . import settings


class SharedLogin(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        user, _, digest = settings.AUTH.partition(":")
        self.user, self.digest = user, digest.lower()

    async def dispatch(self, request, call_next):
        if request.url.path == "/healthz":
            return await call_next(request)
        h = request.headers.get("authorization", "")
        if h.startswith("Basic "):
            try:
                u, _, p = base64.b64decode(h[6:]).decode().partition(":")
                if hmac.compare_digest(u, self.user) and hmac.compare_digest(hashlib.sha256(p.encode()).hexdigest(), self.digest):
                    return await call_next(request)
            except ValueError:
                pass
        return Response("Login required", status_code=401, headers={"WWW-Authenticate": 'Basic realm="SHOTOKAN"'})
