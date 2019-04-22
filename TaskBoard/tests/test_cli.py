# -*- coding: utf-8 -*-
"""
    :suthor: LumiaO
    :url: https://lumia.com
    :copyright: © 2019 LumiaO <zzk1044740758@gmail.com>
    :license: MIT, see LICENSE for more details.
"""

from TaskBoard.models import User, Tag, Project, Milestone, Category, Task, Comment
from TaskBoard.extensions import db
from TaskBoard.tests.base import BaseTestCase


class CLITestCase(BaseTestCase):

    def setUp(self):
        super(CLITestCase, self).setUp()
        db.drop_all()

    def test_initdb_command(self):
        result = self.runner.invoke(args=['initdb'])
        self.assertIn('Initialized database.', result.output)

    def test_initdb_command_with_drop(self):
        result = self.runner.invoke(args=['initdb', '--drop'], input='y\n')
        self.assertIn('This operation will delete the database, do you want to continue?', result.output)
        self.assertIn('Drop tables.', result.output)

    def test_forge_command(self):
        result = self.runner.invoke(args=['forge'])

        self.assertIn('Drop original databases...', result.output)
        self.assertIn('Create new databases...', result.output)
        self.assertIn('Deleting files in uploads...', result.output)

        self.assertEqual(Project.query.count(), 3)
        self.assertIn('Generating 3 projects...', result.output)

        self.assertEqual(User.query.filter_by(is_admin=True).count(), 1)
        self.assertIn('Generating the administrator...', result.output)

        self.assertEqual(Tag.query.count(), 8)
        self.assertIn('Generating 8 tags...', result.output)

        self.assertEqual(User.query.count(), 10 + 1)
        self.assertIn('Generating 10 users...', result.output)

        self.assertIn('Generating 5 milestones for every project ...', result.output)
        self.assertEqual(Milestone.query.count(), 5 * 3)

        self.assertIn('Generating 4 categories for every project ...', result.output)
        self.assertEqual(Category.query.count(), 4 * 3)

        self.assertIn('Generating 4 tasks for every milestone ...', result.output)
        self.assertEqual(Task.query.count(), 4 * 5 * 3)

        self.assertIn('Generating 3 comments for every task ...', result.output)
        self.assertEqual(Comment.query.count(), 3 * 4 * 5 * 3)

        self.assertIn('Done.', result.output)

    def test_forge_command_with_count(self):
        result = self.runner.invoke(
            args=['forge', '--remove', 0, '--project', 4, '--tag', 15, '--user', 15, '--milestone', 4,
                  '--category', 5, '--task', 4, '--comment', 5])

        self.assertIn('Drop original databases...', result.output)
        self.assertIn('Create new databases...', result.output)

        self.assertNotIn('Deleting files in uploads...', result.output)

        self.assertEqual(Project.query.count(), 4)
        self.assertIn('Generating 4 projects...', result.output)

        self.assertEqual(User.query.filter_by(is_admin=True).count(), 1)
        self.assertIn('Generating the administrator...', result.output)

        self.assertEqual(Tag.query.count(), 15)
        self.assertIn('Generating 15 tags...', result.output)

        self.assertEqual(User.query.count(), 15 + 1)
        self.assertIn('Generating 15 users...', result.output)

        self.assertIn('Generating 4 milestones for every project ...', result.output)
        self.assertEqual(Milestone.query.count(), 4 * 4)

        self.assertIn('Generating 5 categories for every project ...', result.output)
        self.assertEqual(Category.query.count(), 5 * 4)

        self.assertIn('Generating 4 tasks for every milestone ...', result.output)
        self.assertEqual(Task.query.count(), 4 * 4 * 4)

        self.assertIn('Generating 5 comments for every task ...', result.output)
        self.assertEqual(Comment.query.count(), 5 * 4 * 4 * 4)

        self.assertIn('Done.', result.output)
