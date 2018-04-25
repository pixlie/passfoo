from sanic.views import HTTPMethodView
from sanic import response
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import IntegrityError

from base.db import db
from base.error_handler import Error, ErrorType
from base.constants import POST_REQUEST, PUT_REQUEST, GET_REQUEST, DELETE_REQUEST


class QueryFilter(object):
    """
    This class provides multiple ways to filter a model.

    The `url_parts` is a mapping of the captured elements from the URL that
    should be used to filter the model.
    `url_parts` maps from the URL part to the field name in model

    If `filter_by_creator` is True, and if the model has a `created_by_id`
    then the model is filtered by current user, which is request.user.id
    """
    url_parts = {}
    filter_by_creator = False
    allowed_filters = []

    def get_default_filters(self, *args, **kwargs):
        pass

    def get_url_parts_filters(self):
        """
        Get a list of SQLAlchemy model filters that we need to apply to get
        the item that we need. The filter values will most probably come
        from URL parts.
        """
        filters = []
        m = self.get_model()
        ua = self.url_parts
        for k, v in self.kwargs.items():
            if k in ua:
                filters.append(ua[k] == self.kwargs[k])
        if self.filter_by_creator and hasattr(m, "created_by_id"):
            filters.append(getattr(m, "created_by_id") == self.request.user.id)
        return filters

    def get_url_query_filters(self, *args, **kwargs):
        pass

    def get_json_filters(self, *args, **kwargs):
        pass

    def get_all_filters(self, *args, **kwargs):
        pass


class SerializerMixin(object):
    model = None
    schema_class = None

    def get_schema(self, instance=None):
        if instance:
            return self.schema_class(instance=instance)
        else:
            return self.schema_class()


class ModelMixin(object):
    def get_model(self):
        return self.model

    def get_item(self):
        return self.get_model().query.filter(*self.get_url_parts_filters()).one()

    def has_related(self):
        m = self.get_model()
        fks = [c for c in m.__table__.columns.values() if c.foreign_keys]
        return True if len(fks) else False


class ListMixin(QueryFilter, SerializerMixin, ModelMixin):
    """
    This mixin is used to get a list of items for a given model.
    """

    def get_list(self):
        if hasattr(self, "get_url_parts_filters"):
            return self.get_model().query.filter(*self.get_url_parts_filters()).all()
        else:
            return self.get_model().query.all()

    def handle_get(self, *args, **kwargs):
        return response.json(
            self.get_schema().dump(self.get_list(), many=True).data
        )


class ViewMixin(QueryFilter, SerializerMixin, ModelMixin):
    """
    This mixin is used to get a single item for a given model.

    When we are reading an item for any model, we require some filters.
    """

    def handle_get(self, *args, **kwargs):
        try:
            return response.json(
                self.get_schema().dump(self.get_item()).data
            )
        except NoResultFound:
            errors = Error.generate_error(type=ErrorType.DATA_NOT_FOUND)
            return response.json(
                errors,
                status=404
            )


class CreateMixin(SerializerMixin, ModelMixin):
    instance = None
    save_creator = True
    related_fields_to_create = None

    def get_insert_defaults(self):
        return {}

    def create_related(self):
        """
        Saves related models of the model that this request is handling.
        Related models should be specified in the schema instance.
        The foreign key relation is maintained.

        Foreign key names are assumed to be ending in "_id" or "_fk"
        """
        m = self.get_model()
        fks = [c for c in m.__table__.columns.values() if c.foreign_keys]
        for c in fks:
            fk = list(c.foreign_keys)[0]
            if c.name[-3:] == "_id" or c.name[-3:] == "_fk":
                name = c.name[:-3]
                if (name in self.related_fields_to_create and
                        hasattr(self.instance, name) and
                        getattr(self.instance, name, None)):
                    fk_instance = getattr(self.instance, name)
                    if(hasattr(fk_instance, "created_from") and self.request.ip):
                        fk_instance.created_from = self.request.ip
                    fk_instance.save(commit=False)
                    # When we use flush, the INSERT query is sent to the
                    # database, but session is not committed now.
                    # The session is committed by the create_instance method
                    # after the parent is also added to session.
                    db.session.flush()
                    fk_id = getattr(fk_instance, fk.column.name)
                    setattr(self.instance, c.name, fk_id)

    def create_instance(self):
        instance = self.instance
        if(hasattr(instance, "created_from") and self.request.ip):
            instance.created_from = self.request.ip
        if (self.save_creator and
                hasattr(instance, "created_by_id") and
                instance.created_by_id is None and self.request.user):
            instance.created_by_id = self.request.user.id
        for k, v in self.get_insert_defaults().items():
            setattr(instance, k, v)
        if hasattr(self, "pre_create"):
            self.pre_create()

        if self.related_fields_to_create and self.has_related():
            self.create_related()

        try:
            instance.save(commit=False)
            if hasattr(self, "pre_create_commit"):
                db.session.flush()
                self.pre_create_commit()

            db.session.commit()
            if hasattr(self, "post_create"):
                self.post_create()
            return True, {}
        except AttributeError as error:
            db.session.rollback()
            error = error.args[0]
            if type(error) == list and "code" in error[0]:
                return False, error
            else:
                return False, Error.generate_error(type=ErrorType.DATABASE_WRITE_FAIL)
        except IntegrityError as i:
            return False, Error.generate_error(data=i, type=ErrorType.DATABASE_WRITE_FAIL)
        except NoResultFound:
            return False, Error.generate_error(type=ErrorType.DATA_NOT_FOUND)

    def handle_post(self, *args, **kwargs):
        schema = self.get_schema()
        schema_instance = schema.load(self.request.json)
        print(self.request.json)
        if not schema_instance.errors:
            self.instance = schema_instance.data
            status, errors = self.create_instance()
            if status:
                return response.json(
                    schema.dump(self.instance).data,
                    status=201
                )
            else:
                return response.json(errors, status=400)
        else:
            print(schema_instance.errors)
            errors = Error.generate_error(
                data=schema_instance.errors,
                type=ErrorType.SCHEMA_ERROR
            )

            return response.json(errors, status=400)


class UpdateMixin(QueryFilter, SerializerMixin, ModelMixin):
    instance = None
    related_fields_to_update = None
    save_creator = True

    def get_update_defaults(self):
        return {}

    def update_related(self):
        """
        Saves related models of the model that this request is handling.
        Related models should be specified in the schema instance.
        The foreign key relation is maintained.

        If the related model already exists then it is updated,
        else a new instance of the related model is created.

        Foreign key names are assumed to be ending in "_id" or "_fk"
        """
        m = self.get_model()
        fks = [c for c in m.__table__.columns.values() if c.foreign_keys]
        for c in fks:
            fk = list(c.foreign_keys)[0]
            if c.name[-3:] == "_id" or c.name[-3:] == "_fk":
                name = c.name[:-3]
                if (name in self.related_fields_to_update and
                        hasattr(self.instance, name) and
                        getattr(self.instance, name, None)):
                    # This instance may have an PK (id) in case the related
                    # model already existed.
                    fk_instance = getattr(self.instance, name)
                    if(hasattr(fk_instance, "created_from") and self.request.ip):
                        fk_instance.created_from = self.request.ip
                    # SQLAlchemy will generate INSERT or UPDATE depending
                    # on the related models existance.
                    fk_instance.save(commit=False)
                    # The following applies only for new related models.
                    # When we use flush, the INSERT query is sent to the
                    # database, but session is not committed now.
                    # The session is committed by the create_instance method
                    # after the parent is also added to session.
                    db.session.flush()
                    fk_id = getattr(fk_instance, fk.column.name)
                    setattr(self.instance, c.name, fk_id)

    def update_instance(self):
        instance = self.instance
        if (self.save_creator and
                hasattr(instance, "updated_by_id") and
                instance.updated_by_id is None and self.request.user):
            instance.updated_by_id = self.request.user.id
        for k, v in self.get_update_defaults().items():
            setattr(instance, k, v)

        try:
            if self.related_fields_to_update and self.has_related():
                self.update_related()
        except AssertionError:
            db.session.rollback()
            return False, Error.generate_error(type=ErrorType.DATABASE_WRITE_FAIL)
        try:
            instance.save(commit=False)

            db.session.commit()
            if hasattr(self, "post_update"):
                self.post_update()
            return True, {}
        except AttributeError as error:
            db.session.rollback()
            error = error.args[0]
            if type(error) == list and "code" in error[0]:
                return False, error
            else:
                return False, Error.generate_error(type=ErrorType.DATABASE_WRITE_FAIL)
        except IntegrityError as i:
            return False, Error.generate_error(data=i, type=ErrorType.DATABASE_WRITE_FAIL)
        except NoResultFound:
            return False, Error.generate_error(type=ErrorType.DATA_NOT_FOUND)

    def handle_put(self, *args, **kwargs):
        try:
            existing = self.get_item()
        except NoResultFound:
            return response.json(Error.generate_error(type=ErrorType.DATA_NOT_FOUND), status=404)
        if hasattr(self, "pre_update"):
            self.pre_update(existing=existing, schema=self.get_schema().load(self.request.json))

        schema = self.get_schema(instance=existing)
        schema_instance = schema.load(self.request.json)

        if not schema_instance.errors:
            self.instance = schema_instance.data
            status, errors = self.update_instance()
            if status:
                return response.json(
                    schema.dump(self.instance).data,
                    status=200
                )
            else:
                return response.json(errors, status=400)
        else:
            errors = Error.generate_error(
                data=schema_instance.errors,
                type=ErrorType.SCHEMA_ERROR
            )
            return response.json(errors, status=400)


class DeleteMixin(QueryFilter, ModelMixin):
    pass


class BaseController(HTTPMethodView):
    request = None
    kwargs = None
    __request_initiated = False

    def init_request(self, request, *args, **kwargs):
        self.request = request
        self.kwargs = kwargs
        self.__request_initiated = True

    async def get(self, request, *args, **kwargs):
        if not self.__request_initiated:
            self.init_request(request, *args, **kwargs)

        if hasattr(self, "handle_get"):
            return self.handle_get(*args, **kwargs)
        else:
            errors = Error.generate_error(data=GET_REQUEST, type=ErrorType.INVALID_METHOD)
            return response.json(
                errors,
                status=405
            )

    async def post(self, request, *args, **kwargs):
        if not self.__request_initiated:
            self.init_request(request, *args, **kwargs)

        if hasattr(self, "handle_post"):
            return self.handle_post(*args, **kwargs)
        else:
            errors = Error.generate_error(data=POST_REQUEST, type=ErrorType.INVALID_METHOD)
            return response.json(
                errors,
                status=405
            )

    async def put(self, request, *args, **kwargs):
        if not self.__request_initiated:
            self.init_request(request, *args, **kwargs)

        if hasattr(self, "handle_put"):
            return self.handle_put(*args, **kwargs)
        else:
            errors = Error.generate_error(data=PUT_REQUEST, type=ErrorType.INVALID_METHOD)
            return response.json(
                errors,
                status=405
            )

    async def delete(self, request, *args, **kwargs):
        if not self.__request_initiated:
            self.init_request(request, *args, **kwargs)

        if hasattr(self, "handle_delete"):
            return self.handle_delete(*args, **kwargs)
        else:
            errors = Error.generate_error(data=DELETE_REQUEST, type=ErrorType.INVALID_METHOD)
            return response.json(
                errors,
                status=405
            )
