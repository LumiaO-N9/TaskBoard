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
import unittest


@unittest.skip('Skip this class temporarily')
class SettingTestCase(BaseTestCase):

    def setUp(self) -> None:
        super(SettingTestCase, self).setUp()
        self.login()

    def test_index(self):
        response = self.client.get(url_for('setting.index'))
        data = response.get_data(as_text=True)
        self.assertIn('TaskBoard-LumiaO', data)
        self.assertIn('Boards', data)
        self.assertIn('Setting', data)
        self.assertIn('Logout', data)
        self.assertIn('User Settings', data)
        self.assertIn('Change Password', data)
        self.assertIn('Change Username', data)
        self.assertIn('Select Default Project', data)
        self.assertIn('Edit Tags', data)
        self.assertIn('TaskBoard Users', data)
        self.assertIn('Project Settings', data)
        self.assertIn('Current Projects', data)

    def test_change_default_project(self):
        fake_Projects()
        fake_Tags()
        fake_Users()
        project = Project.query.get(1)
        project_id = project.id
        with self.client:
            response = self.client.post(url_for('setting.change_default_project'), data=dict(project_id=project_id))
            data = response.get_data(as_text=True)
            self.assertIn('ok', data)
            user_id = current_user.id
            user = User.query.get(user_id)
            self.assertEqual(user.default_project_id, project_id)

    def test_change_user_password(self):
        current_password = "TaskBoard."
        new_password = "HelloFlask."
        with self.client:
            url = url_for('setting.change_user_password')
            data = dict(current_password="wrong-current-password", password=new_password)
            response_data = self.post_data(url, data)
            self.assertIn('invalid', response_data)
            data = dict(current_password=current_password, password=new_password)
            response_data = self.post_data(url, data)
            self.assertIn('ok', response_data)
            self.assertEqual(True, current_user.validate_password(new_password))

    def test_change_user_username_or_email(self):
        fake_Projects()
        fake_Tags()
        fake_Users()
        name = "email"
        same_info = "100001@example.com"
        info = "test@test.email"
        name1 = "username"
        same_info1 = "worker1"
        info1 = "testName"
        with self.client:
            url = url_for('setting.change_user_username_or_email')
            data = dict(name=name, info=same_info)
            response_data = self.post_data(url, data)
            self.assertIn('same', response_data)
            data = dict(name=name1, info=same_info1)
            response_data = self.post_data(url, data)
            self.assertIn('same', response_data)
            data = dict(name=name, info=info)
            response_data = self.post_data(url, data)
            self.assertIn('ok', response_data)
            self.assertIn(current_user.email, info)
            data = dict(name=name1, info=info1)
            response_data = self.post_data(url, data)
            self.assertIn('ok', response_data)
            self.assertIn(current_user.username, info1)

    def test_change_project_status(self):
        fake_Projects()
        project = Project.query.get(1)
        project_id = project.id
        status = project.status
        with self.client:
            url = url_for('setting.change_project_status')
            data = dict(project_id=project_id)
            response_data = self.post_data(url, data)
            self.assertIn('ok', response_data)
            self.assertEqual(status, not project.status)
            data = dict()
            response_data = self.post_data(url, data)
            self.assertIn('None', response_data)

    @unittest.skip("I don't want to run this case")
    def test_sort_by_name(self):
        pass

    @unittest.skip("I don't want to run this case")
    def test_sort_by_date(self):
        pass

    def test_del_user_by_id(self):
        fake_Projects()
        fake_Tags()
        fake_Users()
        user = User.query.filter_by(is_admin=0).first()
        user_id = user.id
        with self.client:
            url = url_for('setting.del_user_by_id')
            data = dict()
            response_data = self.post_data(url, data)
            self.assertIn('None', response_data)
            data = dict(user_id=user_id)
            response_data = self.post_data(url, data)
            self.assertIn('ok', response_data)
            self.assertEqual(None, User.query.get(user_id))

    def test_del_project_by_id(self):
        fake_Projects()
        project = Project.query.get(1)
        project_id = project.id
        with self.client:
            url = url_for('setting.del_project_by_id')
            data = dict()
            response_data = self.post_data(url, data)
            self.assertIn('None', response_data)
            data = dict(project_id=project_id)
            response_data = self.post_data(url, data)
            self.assertIn('ok', response_data)
            self.assertEqual(None, Project.query.get(project_id))

    def test_save_user_edit_modal(self):
        fake_Projects()
        fake_Tags()
        fake_Users()
        user_id_not_exist = -1
        user = User.query.filter_by(is_admin=0).first()
        user_id_exist = user.id
        new_username = 'testName'
        new_password = 'HelloFlask.'
        new_email = 'test@Test.test'
        new_tag_id = 1
        new_default_project_id = 1
        new_access_project_id = 1
        new_is_admin = 1
        add_status = 'add'
        edit_status = 'edit'
        with self.client:
            url = url_for('setting.save_user_edit_modal')
            # test None
            data = dict(user_id=user_id_not_exist)
            response_data = self.post_data(url, data)
            self.assertIn('None', response_data)
            # test add
            data = dict(
                username=new_username,
                password1=new_password,
                email=new_email,
                tag=new_tag_id,
                default_project=new_default_project_id,
                access_project=new_access_project_id,
                is_admin=new_is_admin
            )
            response_data = self.post_data(url, data)
            self.assertIn(add_status, response_data)
            new_user = User.query.filter_by(username=new_username).first()
            self.assertEqual(new_user.username, new_username)
            self.assertEqual(new_user.validate_password(new_password), True)
            self.assertEqual(new_user.email, new_email)
            self.assertEqual(new_user.tag_id, new_tag_id)
            self.assertEqual(new_user.default_project_id, new_default_project_id)
            self.assertEqual(new_user.access_project_id, new_access_project_id)
            self.assertEqual(new_user.is_admin, 1)
            # test edit
            data = dict(
                user_id=user_id_exist,
                username=new_username,
                password1=new_password,
                email=new_email,
                tag=new_tag_id,
                default_project=new_default_project_id,
                access_project=new_access_project_id,
                is_admin=new_is_admin
            )
            response_data = self.post_data(url, data)
            self.assertIn('same username', response_data)
            data['username'] = data['username'] + 'New'
            response_data = self.post_data(url, data)
            self.assertIn('same email', response_data)
            data['email'] = data['email'] + 'New'
            response_data = self.post_data(url, data)
            self.assertIn(edit_status, response_data)
            new_user = User.query.get(user_id_exist)
            self.assertEqual(new_user.username, data['username'])
            self.assertEqual(new_user.validate_password(new_password), True)
            self.assertEqual(new_user.email, data['email'])
            self.assertEqual(new_user.tag_id, new_tag_id)
            self.assertEqual(new_user.default_project_id, new_default_project_id)
            self.assertEqual(new_user.access_project_id, new_access_project_id)
            self.assertEqual(new_user.is_admin, 1)

    @unittest.skip("I don't want to run this case")
    def test_ajax_load_project_table(self):
        pass

    @unittest.skip("I don't want to run this case")
    def test_ajax_load_user_table(self):
        pass

    def test_add_tag(self):
        fake_Tags()
        tag_name = "NewTag"
        with self.client:
            url = url_for('setting.add_tag')
            data = dict()
            response_data = self.post_data(url, data)
            self.assertIn('None', response_data)
            data = dict(tag=tag_name)
            response_data = self.post_data(url, data)
            self.assertIn('ok', response_data)
            response_data = self.post_data(url, data)
            self.assertIn('same', response_data)

    def test_edit_tag(self):
        fake_Tags()
        tag_name = 'NewTag'
        tag = Tag.query.get(1)
        tag_id = tag.id
        with self.client:
            url = url_for('setting.edit_tag')
            data = dict()
            response_data = self.post_data(url, data)
            self.assertIn('None', response_data)
            data = dict(tag=tag_name, tag_id=tag_id)
            response_data = self.post_data(url, data)
            self.assertIn('ok', response_data)
            self.assertEqual(tag.tag, tag_name)
            data = dict(tag=tag_name, tag_id=tag_id + 1)
            response_data = self.post_data(url, data)
            self.assertIn('same', response_data)

    def test_delete_tag(self):
        fake_Tags()
        tag = Tag.query.get(1)
        tag_id = tag.id
        with self.client:
            url = url_for('setting.delete_tag')
            data = dict()
            response_data = self.post_data(url, data)
            self.assertIn('None', response_data)
            data = dict(tag_id=tag_id)
            response_data = self.post_data(url, data)
            self.assertIn('ok', response_data)
            self.assertEqual(None, Tag.query.get(tag_id))

    def test_save_project_edit_modal(self):
        fake_Projects()
        fake_Tags()
        fake_Users()
        fake_milestones()
        fake_categories()
        last_milestone_id = Milestone.query.order_by(Milestone.id.desc()).first().id
        last_category_id = Category.query.order_by(Category.id.desc()).first().id
        project = Project.query.get(1)
        project_milestones = project.milestones
        project_categories = project.categories
        users = User.query.all()
        project_id = project.id
        project_title = 'NewProjectTitle'
        order_id_array = []
        exist_milestones_id_title = {}
        exist_categories_id_title_color = {}
        wait_to_delete_milestone_id_array = []
        wait_to_delete_category_id_array = []
        wait_remove_users_id_array = []
        wait_add_users_id_array = []
        for i in range(len(users)):
            user_id_tmp = users[i].id
            if i % 2 == 0:
                wait_remove_users_id_array.append(str(user_id_tmp))
            else:
                wait_add_users_id_array.append(str(user_id_tmp))
        for i in range(len(project.milestones)):
            milestone_id_tmp = project_milestones[i].id
            if i % 2 == 0:
                wait_to_delete_milestone_id_array.append(str(milestone_id_tmp))
            else:
                order_id_array.append(str(milestone_id_tmp))
                last_milestone_id = last_milestone_id + 1
                order_id_array.append(str(last_milestone_id))
                exist_milestones_id_title[str(milestone_id_tmp)] = 'newMilestoneTitle' + str(milestone_id_tmp)
                exist_milestones_id_title[str(last_milestone_id)] = 'newMilestoneTitle' + str(last_milestone_id)
        for i in range(len(project_categories)):
            category_id_tmp = project_categories[i].id
            if i == 1:
                wait_to_delete_category_id_array.append(str(project_categories[i].id))
                exist_categories_id_title_color[str(last_category_id + 1)] = {'title': 'CategoryTitleTest',
                                                                              'color': '#888888'}
            else:
                exist_categories_id_title_color[str(category_id_tmp)] = {
                    'title': 'CategoryTitleTest' + str(category_id_tmp),
                    'color': '#888888'}
        json_data_none = {
            'project_title': "",
            'order_id_array': [],
            'exist_milestones_id_title': {},
            'exist_categories_id_title_color': {},
            'wait_to_delete_milestone_id_array': [],
            'wait_to_delete_category_id_array': [],
            'wait_remove_users_id_array': [],
            'wait_add_users_id_array': [],
        }
        json_data = {
            'project_id': project_id,
            'project_title': project_title,
            'order_id_array': order_id_array,
            'exist_milestones_id_title': exist_milestones_id_title,
            'exist_categories_id_title_color': exist_categories_id_title_color,
            'wait_to_delete_milestone_id_array': wait_to_delete_milestone_id_array,
            'wait_to_delete_category_id_array': wait_to_delete_category_id_array,
            'wait_remove_users_id_array': wait_remove_users_id_array,
            'wait_add_users_id_array': wait_add_users_id_array,
        }
        url = url_for('setting.save_project_edit_modal')
        with self.client:
            response = self.client.post(url, json=json_data_none)
            response_data = response.get_data(as_text=True)
            self.assertIn('add', response_data)
            response = self.client.post(url, json=json_data)
            response_data = response.get_data(as_text=True)
            self.assertIn('edit', response_data)
            project = Project.query.get(project_id)
            self.assertEqual(project_title, project.title)
            users_array = []
            for user in project.users:
                users_array.append(str(user.id))
            self.assertEqual(wait_add_users_id_array, users_array)
            original_milestones_name = [value for value in exist_milestones_id_title.values()]
            for milestone in project.milestones:
                self.assertIn(milestone.title, original_milestones_name)
            original_categories_name = [value['title'] for value in exist_categories_id_title_color.values()]
            for category in project.categories:
                self.assertIn(category.title, original_categories_name)
                self.assertEqual(category.color, '#888888')
