from sqlalchemy import Column, DateTime, Integer, ForeignKey, text
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.dialects.postgresql import INET
from sqlalchemy.orm.query import Query

from base.db import db, Base


class classproperty(object):
    def __init__(self, fget):
        self.fget = fget

    def __get__(self, owner_self, owner_cls):
        return self.fget(owner_cls)


class SystemModel(Base):
    """
    Inherit from this base model if you do not need any default fields in your inherited class.
    It contains the unique and primary key ID field which is mandatory in all models.
    """

    __abstract__ = True

    id = Column(Integer, primary_key=True)

    def __init__(self, *args, **kwargs):
        for obj in kwargs.items():
            setattr(self, obj[0], obj[1])

    @classproperty
    def query(cls):
        return Query([cls], session=db.session)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def save(self, commit=True):
        db.session.add(self)

        if commit:
            try:
                db.session.commit()
            except Exception:
                db.session.rollback()
                raise
        else:
            db.session.flush()


class BaseModel(SystemModel):
    """
    This is our base model for all other models that are owned by a user.
    It tracks the user who created any record, when and from which IP address.
    """
    __abstract__ = True

    created_at = Column(DateTime, nullable=False, server_default=text("(now() at time zone 'utc')"))
    created_from = Column(INET, nullable=False)

    def __init__(self, *args, **kwargs):
        for obj in kwargs.items():
            setattr(self, obj[0], obj[1])

    @declared_attr
    def created_by_id(self):
        return Column(Integer, ForeignKey("user.id", name="created_by_fk"), nullable=False)
