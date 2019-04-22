# -*- coding: utf-8 -*-
"""
    :suthor: LumiaO
    :url: https://lumia.com
    :copyright: © 2019 LumiaO <zzk1044740758@gmail.com>
    :license: MIT, see LICENSE for more details.
"""

from flask import url_for
from flask_login import current_user
from TaskBoard.tests.base import BaseTestCase
from TaskBoard.fakes import *


class BoardTestCase(BaseTestCase):
    def setUp(self) -> None:
        super(BoardTestCase, self).setUp()
        self.login()

    def test_index(self):
        response = self.client.get(url_for('taskboard.index'))
        data = response.get_data(as_text=True)
        self.assertIn('TaskBoard-LumiaO', data)
        self.assertIn('Boards', data)
        self.assertIn('Setting', data)
        self.assertIn('Logout', data)
        self.assertIn('Project Tree', data)
        self.assertIn('Milestone Column', data)
        self.assertIn('Task Column', data)

    def test_none_project(self):
        response = self.client.get(url_for('taskboard.none_project'))
        data = response.get_data(as_text=True)
        self.assertIn('There is not exist any project. ', data)

    def test_render_milestone_column(self):
        fake_Projects(1)
        fake_milestones(1)
        project = Project.query.get(1)
        project_id = project.id
        data = dict(project_id=project_id)
        with self.client:
            url = url_for('taskboard.render_milestone_column')
            response_data = self.post_data(url, data=dict(project_id='None'))
            self.assertIn('There is no default project', response_data)
            response_data = self.post_data(url, data=data)
            self.assertNotIn('There is no default project', response_data)

    def test_render_task_column(self):
        fake_Projects(1)
        fake_Tags(1)
        fake_Users(1)
        fake_milestones(1)
        fake_categories(1)
        fake_tasks(1)
        task = Task.query.get(1)
        task_id = task.id
        data = dict(task_id=task_id)
        with self.client:
            url = url_for('taskboard.render_task_column')
            response_data = self.post_data(url, data=None)
            self.assertNotIn('Description', response_data)
            self.assertNotIn('Add Attachment', response_data)
            self.assertNotIn('Add Comment', response_data)
            response_data = self.post_data(url, data=data)
            self.assertIn('Description', response_data)
            self.assertIn('Add Attachment', response_data)
            self.assertIn('Add Comment', response_data)

    def test_save_task_edit_modal(self):
        fake_Projects(1)
        fake_Tags(1)
        fake_Users(1)
        fake_milestones(1)
        fake_categories(1)
        fake_tasks(1)
        action_type_edit = 'edit'
        action_type_add = 'add'
        task_id = 1
        task_name = 'newTaskNameTest'
        task_description = 'emmmmmmmmmmmmmmm'
        assigned_user_id = 1
        category_id = 1
        milestone_id = 1
        color_text = '#888888'
        date_picker_text = '2019-10-24'
        points = 6

        json_data = {
            'action_type': action_type_edit,
            'task_id': task_id,
            'task_name': task_name,
            'task_description': task_description,
            'assigned_user_id': assigned_user_id,
            'category_id': category_id,
            'milestone_id': milestone_id,
            'color_text': color_text,
            'date_picker_text': date_picker_text,
            'points': points
        }
        url = url_for('taskboard.save_task_edit_modal')
        with self.client:
            response = self.client.post(url, json=json_data)
            response_data = response.get_data(as_text=True)
            self.assertIn('edit-' + str(task_id), response_data)
            task = Task.query.get(task_id)
            self.assertEqual(task_name.title(), task.title)
            self.assertEqual(task_description, task.description)
            self.assertEqual(assigned_user_id, task.user_id)
            self.assertEqual(category_id, task.category_id)
            self.assertEqual(milestone_id, task.milestone_id)
            self.assertEqual(color_text, task.color)
            self.assertEqual(date_picker_text, task.due_date.strftime('%Y-%m-%d'))
            self.assertEqual(points, task.points)
            json_data['action_type'] = action_type_add
            response = self.client.post(url, json=json_data)
            response_data = response.get_data(as_text=True)
            task_id = response_data.split('-')[1]
            self.assertIn('add-' + str(task_id), response_data)
            task = Task.query.get(task_id)
            self.assertEqual(task_name.title(), task.title)
            self.assertEqual(task_description, task.description)
            self.assertEqual(assigned_user_id, task.user_id)
            self.assertEqual(category_id, task.category_id)
            self.assertEqual(milestone_id, task.milestone_id)
            self.assertEqual(color_text, task.color)
            self.assertEqual(date_picker_text, task.due_date.strftime('%Y-%m-%d'))
            self.assertEqual(points, task.points)

    def test_add_milestone_node(self):
        project_id = 1
        milestone_name = 'NewMilestoneName'
        with self.client:
            url = url_for('taskboard.add_milestone_node')
            response_data = self.post_data(url, data=dict(parent_id='None'))
            self.assertIn('fail', response_data)
            response_data = self.post_data(url, data=dict(parent_id=project_id, new_name=milestone_name))
            self.assertIn('ok', response_data)
            milestone = Milestone.query.filter_by(title=milestone_name.title()).first()
            self.assertEqual(milestone_name.title(), milestone.title)
            self.assertEqual(project_id, milestone.project_id)

    def test_rename_node(self):
        fake_Projects(1)
        fake_Tags(1)
        fake_Users(1)
        fake_milestones(1)
        fake_categories(1)
        fake_tasks(1)
        node_type = 'None'
        node_id = 1
        new_name = 'NewNameTest'.title()
        data = dict(type=node_type, id=node_id, new_name=new_name)
        with self.client:
            url = url_for('taskboard.rename_node')
            response_data = self.post_data(url, data=data)
            self.assertIn('None', response_data)
            data['type'] = 'task'
            response_data = self.post_data(url, data=data)
            self.assertIn('ok', response_data)
            task = Task.query.get(node_id)
            self.assertEqual(new_name, task.title)
            data['type'] = 'milestone'
            response_data = self.post_data(url, data=data)
            self.assertIn('ok', response_data)
            milestone = Milestone.query.get(node_id)
            self.assertEqual(new_name, milestone.title)
            data['type'] = 'project'
            response_data = self.post_data(url, data=data)
            self.assertIn('ok', response_data)
            project = Project.query.get(node_id)
            self.assertEqual(new_name, project.title)

    def test_copy_node(self):
        fake_Projects(1)
        fake_Tags(1)
        fake_Users(1)
        fake_milestones(1)
        fake_categories(1)
        fake_tasks(1)
        node_type = 'None'
        node_id = 1
        new_name = 'NewNameTest'.title()
        target_id = 1
        data = dict(type=node_type, id=node_id, new_name=new_name, target_id=target_id)
        with self.client:
            url = url_for('taskboard.copy_node')
            response_data = self.post_data(url, data=data)
            self.assertIn('None', response_data)
            data['type'] = 'task'
            response_data = self.post_data(url, data=data)
            self.assertIn('ok', response_data)
            task = Task.query.get(node_id)
            new_task = Task.query.filter_by(title=new_name).first()
            self.assertEqual(new_task.title, new_name)
            self.assertEqual(new_task.description, task.description)
            self.assertEqual(new_task.color, task.color)
            self.assertEqual(new_task.due_date, task.due_date)
            self.assertEqual(new_task.points, task.points)
            self.assertEqual(new_task.milestone_id, target_id)
            self.assertEqual(new_task.category_id, task.category_id)
            self.assertEqual(new_task.user_id, task.user_id)
            data['type'] = 'milestone'
            response_data = self.post_data(url, data=data)
            self.assertIn('ok', response_data)
            new_milestone = Milestone.query.filter_by(title=new_name).first()
            self.assertEqual(new_milestone.title, new_name)
            self.assertEqual(new_milestone.project_id, target_id)

    def test_move_node(self):
        fake_Projects(1)
        fake_Tags(1)
        fake_Users(1)
        fake_milestones(1)
        fake_categories(1)
        fake_tasks(1)
        node_type = 'None'
        node_id = 1
        target_id = 1
        data = dict(type=node_type, id=node_id, target_id=target_id)
        with self.client:
            url = url_for('taskboard.move_node')
            response_data = self.post_data(url, data=data)
            self.assertIn('None', response_data)
            data['type'] = 'task'
            response_data = self.post_data(url, data=data)
            self.assertIn('ok', response_data)
            task = Task.query.get(node_id)
            self.assertEqual(task.milestone_id, target_id)
            data['type'] = 'milestone'
            response_data = self.post_data(url, data=data)
            self.assertIn('ok', response_data)
            milestone = Milestone.query.get(node_id)
            self.assertEqual(milestone.project_id, target_id)

    def test_delete_node(self):
        fake_Projects(1)
        fake_Tags(1)
        fake_Users(1)
        fake_milestones(1)
        fake_categories(1)
        fake_tasks(1)
        node_type = 'None'
        node_id = 1
        data = dict(type=node_type, id=node_id)
        with self.client:
            url = url_for('taskboard.delete_node')
            response_data = self.post_data(url, data=data)
            self.assertIn('None', response_data)
            data['type'] = 'task'
            response_data = self.post_data(url, data=data)
            self.assertIn('ok', response_data)
            self.assertEqual(Task.query.get(node_id), None)
            data['type'] = 'milestone'
            response_data = self.post_data(url, data=data)
            self.assertIn('ok', response_data)
            self.assertEqual(Milestone.query.get(node_id), None)
            data['type'] = 'project'
            response_data = self.post_data(url, data=data)
            self.assertIn('ok', response_data)
            self.assertEqual(Project.query.get(node_id), None)

    def test_task_attachment_upload(self):
        pass

    def test_download_task_attachment(self):
        pass

    def test_delete_task_attachment(self):
        pass

    def test_edit_or_add_comment(self):
        fake_Projects(1)
        fake_Tags(1)
        fake_Users(1)
        fake_milestones(1)
        fake_categories(1)
        fake_tasks(1)
        fake_comments(1)
        action = 'None'
        text = 'balabalabalabalabalabala'
        task_id = 1
        data = dict(action=action, text=text, task_id=task_id)
        with self.client:
            url = url_for('taskboard.edit_or_add_comment')
            response_data = self.post_data(url, data=data)
            self.assertIn('fail', response_data)
            data['action'] = 'add'
            response_data = self.post_data(url, data=data)
            self.assertIn('add', response_data)
            comment = Comment.query.filter_by(text=text).first()
            self.assertEqual(comment.user_id, current_user.id)
            self.assertEqual(comment.task_id, task_id)
            data['action'] = 'edit'
            data['comment_id'] = 1
            response_data = self.post_data(url, data=data)
            self.assertIn('edit', response_data)
            comment = Comment.query.get(1)
            self.assertEqual(comment.user_id, current_user.id)
            self.assertEqual(comment.task_id, task_id)
            self.assertEqual(comment.text, text)

    def test_delete_comment_by_id(self):
        fake_Projects(1)
        fake_Tags(1)
        fake_Users(1)
        fake_milestones(1)
        fake_categories(1)
        fake_tasks(1)
        fake_comments(1)
        comment_id = 1
        with self.client:
            url = url_for('taskboard.delete_comment_by_id')
            response_data = self.post_data(url, data=None)
            self.assertIn('None', response_data)
            response_data = self.post_data(url, data=dict(comment_id=comment_id))
            self.assertIn('ok', response_data)
            self.assertEqual(None, Comment.query.get(comment_id))
