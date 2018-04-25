import datetime
from sqlalchemy import (
    Column, DateTime, Integer, create_engine
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker, Query

from base.config import settings
from base.singleton import Singleton


class classproperty(object):
    def __init__(self, fget):
        self.fget = fget

    def __get__(self, owner_self, owner_cls):
        return self.fget(owner_cls)


class DB(metaclass=Singleton):
    __engine = None
    __scoped_session = None
    __test_mode = True

    @property
    def engine(self):
        if self.__engine is None:
            if self.__test_mode:
                self.__engine = create_engine(
                    settings.DATABASES['test'],
                    convert_unicode=True
                )
            else:
                self.__engine = create_engine(
                    settings.DATABASES['default'],
                    convert_unicode=True
                )
        return self.__engine

    @property
    def session(self):
        if self.__scoped_session is None:
            Session = scoped_session(sessionmaker(
                autocommit=False
            ))
            Session.configure(bind=self.engine)
            self.__scoped_session = Session
        return self.__scoped_session()

    def remove_session(self):
        # A good post about this:
        # http://kronosapiens.github.io/blog/2014/07/29/setting-up-unit-tests-with-flask.html
        if self.__scoped_session is not None:
            self.__scoped_session.remove()

    def test_mode(self):
        self.__test_mode = True
        self.__engine = None

    def production_mode(self):
        self.__test_mode = False
        self.__engine = None

    @property
    def is_test_mode(self):
        return self.__test_mode


db = DB()

Base = declarative_base()


class Model(Base):
    __abstract__ = True

    id = Column(Integer, primary_key=True)
    created_at = Column(
        DateTime,
        nullable=False,
        default=datetime.datetime.utcnow
    )

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
