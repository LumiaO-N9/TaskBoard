# -*- coding: utf-8 -*-
"""
    :suthor: LumiaO
    :url: https://lumia.com
    :copyright: © 2019 LumiaO <zzk1044740758@gmail.com>
    :license: MIT, see LICENSE for more details.
"""

from flask import url_for
from TaskBoard.tests.base import BaseTestCase


class AuthTestCase(BaseTestCase):

    def test_login_user(self):
        response = self.login()
        data = response.get_data(as_text=True)
        self.assertIn('/', data)

    def test_invalid_login(self):
        response = self.login(username="LumiaO", password="wrong-password")
        data = response.get_data(as_text=True)
        self.assertIn('invalid', data)

    def test_danger_login(self):
        response = self.login(username="wrong-username", password="wrong-password")
        data = response.get_data(as_text=True)
        self.assertIn('danger', data)

    def test_login_protect(self):
        response = self.client.get(url_for('taskboard.index'), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Please log in to access this page.', data)

    def test_logout(self):
        self.login()
        response = self.client.get(url_for('auth.logout'), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Logout success.', data)
        self.test_login_protect()
