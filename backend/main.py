#!/usr/bin/env python3
import os.path
import argparse
from sqlalchemy.schema import MetaData
from alembic.config import Config
from alembic import command
import importlib

from base.config import settings
from base.db import db, Base
from apps import app


def create_tables(args):
    app.load_models()
    Base.metadata.create_all(db.engine)


def drop_tables(args):
    answer = input("Are you sure you want to run this command. It will "
                   "drop all tables in the database(y/n):")

    if answer == 'y':
        md = MetaData(bind=db.engine, reflect=True)
        md.drop_all()

    print("Tables have been droppped successfully")


def migrate(args):
    alembic_cfg = Config(os.path.join(settings.BASE_DIR, "alembic.ini"))
    with db.engine.begin() as connection:
        alembic_cfg.attributes['connection'] = connection
        command.upgrade(alembic_cfg, "head")


def resetdb(args):
    answer = input("Are you sure you want to run this command. It will "
                   "reset and migrate the database(y/n):")

    if answer == 'y':
        md = MetaData(bind=db.engine, reflect=True)
        md.drop_all()

        alembic_cfg = Config(os.path.join(settings.BASE_DIR, "alembic.ini"))
        with db.engine.begin() as connection:
            alembic_cfg.attributes['connection'] = connection
            command.upgrade(alembic_cfg, "head")
        print("Database has been reset successfully")


def load_fixtures(args):
    for app in settings.APPS:
        try:
            fixtures = importlib.import_module("apps.%s.fixtures" % app)
            if hasattr(fixtures, "generate"):
                fixtures.generate()
        except ModuleNotFoundError:
            pass


if __name__ == '__main__':
    db.production_mode()
    from apps import app
    parser = argparse.ArgumentParser(description="default backend")
    parser.add_argument(
        "action",
        action="store",
        choices=["server", "droptables", "resetdb", "migrate", "consumer",
                 "createtags", "createtables", "loadfixtures"]
    )

    args = parser.parse_args()

    if args.action == "server":
        app.run(**settings.DAEMON)
    elif args.action == "resetdb":
        resetdb(args)
    elif args.action == "droptables":
        drop_tables(args)
    elif args.action == "migrate":
        migrate(args)
    elif args.action == "consumer":
        from message_queue.consumer import run_worker
        run_worker()
    elif args.action == "createtags":
        create_sample_tags()
    elif args.action == "createtables":
        create_tables(args)
    elif args.action == "loadfixtures":
        load_fixtures(args)
