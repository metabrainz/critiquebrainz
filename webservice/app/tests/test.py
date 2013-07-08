import unittest
from flask import Flask
from flask.ext.testing import TestCase
from sqlalchemy.engine.url import URL
from app.utils import UUIDConverter
from app import app, db, fixtures, models, views

class AppTestCase(TestCase):

    def create_app(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = \
            str(app.config['SQLALCHEMY_DATABASE_URI'])+'_test'
        app.config['TESTING'] = True
        UUIDConverter._register(app)
        views.register_views(app)
        return app

    def setUp(self):
        models.create_tables(self.app)
        fixtures.install(self.app, *fixtures.all_data)
        self.db = models.init_app(self.app)

    def tearDown(self):
        self.db.session.remove()
        self.db.drop_all()
