# -*- coding: utf-8 -*-
"""
    :suthor: LumiaO
    :url: https://lumia.com
    :copyright: © 2019 LumiaO <zzk1044740758@gmail.com>
    :license: MIT, see LICENSE for more details.
"""

import unittest

from flask import url_for
from TaskBoard import create_app
from TaskBoard.extensions import db
from TaskBoard.models import User


class BaseTestCase(unittest.TestCase):

    def setUp(self) -> None:
        app = create_app('testing')
        self.context = app.test_request_context()
        self.context.push()
        self.client = app.test_client()
        self.runner = app.test_cli_runner()

        db.create_all()
        user = User(username='LumiaO', is_admin=1, email='LumiaO@NOKIA.com')
        user.set_password('TaskBoard.')
        db.session.add(user)
        db.session.commit()

    def tearDown(self) -> None:
        db.drop_all()
        self.context.pop()

    def login(self, username=None, password=None):
        if username is None and password is None:
            username = "LumiaO"
            password = "TaskBoard."
        status = self.client.post(url_for('auth.login'), data=dict(username=username, password=password))
        return status

    def logout(self):
        return self.client.get(url_for('auth.logout'), follow_redirects=True)
