import uuid
from functools import partial, wraps
from inspect import isawaitable
from pymemcache.client.base import Client

from sanic import response
from sanic_auth import Auth
from base.config import settings


class CustomAuth(Auth):
    __session_client__ = None

    def session_store(self):
        if not self.__session_client__:
            self.__session_client__ = Client((settings.MEMCACHE_HOST, 11211))
        return self.__session_client__

    def set_auth_token(self, request, auth_token=None):
        auth_header = request.headers.get("authorization", None)
        if auth_header:
            _, auth_token = auth_header.split(" ")
        if auth_token is None:
            auth_token = uuid.uuid4().hex
        self.auth_session_key = auth_token

    def login_user(self, request, user, auth_token=None):
        if auth_token:
            self.set_auth_token(request, auth_token)
            self.session_store().set(self.auth_session_key, self.serialize(user))
        else:
            self.session_store().set(self.auth_session_key, self.serialize(user))
        return self.auth_session_key

    def serialize(self, user):
        return user.id

    def load_user(self, token):
        from apps.account.models import User
        return User.query.filter(User.id == token).first()

    def current_user(self, request):
        if "authorization" in request.headers:
            _, token = request.headers["authorization"].split(" ")
            user_id = self.session_store().get(token)
            if user_id is not None:
                return self.load_user(int(user_id))
        return None

    def logout_user(self, request):
        data = self.session_store().get(self.auth_session_key)
        self.session_store().delete(self.auth_session_key)
        return data

    def login_required(
            self,
            route=None,
            user_keyword=None,
            handle_no_auth=None):
        if route is None:
            return partial(self.login_required, user_keyword=user_keyword,
                           handle_no_auth=handle_no_auth)

        if handle_no_auth is not None:
            assert callable(handle_no_auth), 'handle_no_auth must be callable'

        @wraps(route)
        async def privileged(*args, **kwargs):
            if len(args) == 1:
                request, = args
            elif len(args) == 2:
                _, request = args
            user = self.current_user(request)
            if isawaitable(user):
                user = await user

            if user is None:
                if handle_no_auth:
                    resp = handle_no_auth(request)
                else:
                    resp = self.handle_no_auth(request)
            else:
                if user_keyword is not None:
                    if user_keyword in kwargs:
                        raise RuntimeError(
                            'override user keyword %r in route' % user_keyword)
                    kwargs[user_keyword] = user
                resp = route(*args, **kwargs)

            if isawaitable(resp):
                resp = await resp
            return resp

        return privileged

    def handle_no_auth(self, request):
        return response.json(dict(message='unauthorized'), status=401)

    def handle_no_authorization(self, request):
        return response.json(dict(message='unauthorized'), status=403)

    def owner_required(
            self,
            object_to_check=None,
            owner_field='created_by_id',
            allowed_user_ids=None):
        """
        This decorator can be used to limit access to an API endpoint method
        only to the owner of the object.

        :param object_to_check: the model object we are checking
        :param owner_field: which field in the object is owner ID (default created_by_id)
        """
        def actual_decorator(
                route=None,
                user_keyword=None):
            if route is None:
                return partial(self.login_required, user_keyword=user_keyword)

            @wraps(route)
            async def privileged(*args, **kwargs):
                if len(args) == 1:
                    request, = args
                elif len(args) == 2:
                    _, request = args
                user = self.current_user(request)
                if isawaitable(user):
                    user = await user

                if user is None:
                    resp = self.handle_no_auth(request)
                elif not object_to_check and allowed_user_ids and user.id not in allowed_user_ids:
                    resp = self.handle_no_authorization(request)
                elif object_to_check and user.id != getattr(object_to_check, owner_field):
                    resp = self.handle_no_authorization(request)
                else:
                    if user_keyword is not None:
                        if user_keyword in kwargs:
                            raise RuntimeError(
                                'override user keyword %r in route' % user_keyword)
                        kwargs[user_keyword] = user
                    resp = route(*args, **kwargs)

                if isawaitable(resp):
                    resp = await resp
                return resp

            return privileged
        return actual_decorator


def login_required(func, *args, **kwargs):
    """
    This is a decorator that can be applied to a Controller method that needs a logged in user.
    The inner method receives the Controller instance and checks if the user is logged in
    using the `request.is_authenticated` Boolean on the Controller instance

    :param func: The is the function being decorated.
    :return: Either the method that is decorated (if user is logged in) else `unauthenticated` response (HTTP 401).
    """
    def inner(controller_obj, *args, **kwargs):
        if controller_obj.request.is_authenticated:
            return func(controller_obj, *args, **kwargs)
        else:
            return response.json({
                "message": "unauthenticated"
            }, status=401)

    return inner


def owner_required(func, *args, **kwargs):
    """
    This is a decorator that can be applied to a Controller method that needs to test the ownership of
    an object before allowing a succesful response. It first checks if the user is logged in and
    then goes ahead to check if the object is owned by the current user.

    The current object is fetched using the Controller instance's `get_item` method.
    It is assumed that the item has a property `created_by_id` and this should match the `id` of the
    `request.user`.

    :param func: The is the function being decorated.
    :return: Either the method that is decorated (if user is logged in and owner). If the user is not
        logged in then the return is a `unauthenticated` response (HTTP 401). If the user is not the owner then
        the return is a `unauthorized` response (HTTP 403).
    """
    def inner(controller_obj, *args, **kwargs):
        if controller_obj.request.is_authenticated:
            if controller_obj.get_item().created_by_id == controller_obj.request.user.id:
                return func(controller_obj, *args, **kwargs)
            else:
                return response.json({
                    "message": "unauthorized"
                }, status=403)
        else:
            return response.json({
                "message": "unauthenticated"
            }, status=401)

    return inner


def permission_check_required(func):
    def inner(controller_obj, *args, **kwargs):
        if controller_obj.permission_check():
            return func(controller_obj, *args, **kwargs)
        else:
            return response.json({
                "message": "unauthorized"
            }, status=403)

    return inner
