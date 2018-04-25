from sanic import Sanic
from sanic.request import Request
from sanic.response import json
import importlib

from base.config import settings
from base.singleton import Singleton
from base.auth import CustomAuth
import apps.password.urls


async def main_route(request):
    return json({
        "message": "Human way to manage cryptic passwords"
    })


class CustomRequest(Request):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = None

    @property
    def is_authenticated(self):
        return self.user is not None


class CustomApp(Sanic, metaclass=Singleton):
    def setup_routes(self):
        self.add_route(main_route, "/")

        for app in settings.APPS:
            try:
                urls = importlib.import_module("apps.%s.urls" % app)
                if hasattr(urls, "add_routes"):
                    urls.add_routes(self)
            except ModuleNotFoundError:
                pass

    def add_route(self, *args, **kwargs):
        # Prepend /api to all API URLs by default
        prepend = kwargs.pop("prepend", "/api")
        uri = "%s%s" % (prepend, args[1])
        super().add_route(args[0], uri, **kwargs)

    def load_models(self):
        models = []
        for app in settings.APPS:
            try:
                models.append(importlib.import_module("apps.%s.models" % app))
            except ModuleNotFoundError:
                pass
        return models


app = CustomApp(__name__, request_class=CustomRequest)
app.config.AUTH_LOGIN_ENDPOINT = "login"
app.config.SECRET_KEY = settings.SECRET_KEY
auth = CustomAuth(app)


def session_middleware(request):
    auth.set_auth_token(request)
    user = auth.current_user(request)
    if user:
        request.user = user
    else:
        request.user = None


app.register_middleware(session_middleware, attach_to='request')
app.setup_routes()
