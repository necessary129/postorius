# -*- coding: utf-8 -*-
# Copyright (C) 2012-2015 by the Free Software Foundation, Inc.
#
# This file is part of Postorius.
#
# Postorius is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option)
# any later version.
# Postorius is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along with
# Postorius.  If not, see <http://www.gnu.org/licenses/>.
from __future__ import absolute_import, print_function, unicode_literals

from django.conf import settings
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from six.moves.urllib_parse import quote

from postorius.tests.utils import ViewTestCase
from postorius.utils import get_client
from postorius.forms import MemberModeration, UserPreferences


class ListMembersOptionsTest(ViewTestCase):
    """Tests for the list members page.

    Tests permissions and creation of list owners and moderators.
    """

    def setUp(self):
        super(ListMembersOptionsTest, self).setUp()
        self.domain = get_client().create_domain('example.com')
        self.foo_list = self.domain.create_list('foo')
        self.user = User.objects.create_user(
            'testuser', 'test@example.com', 'testpass')
        self.superuser = User.objects.create_superuser(
            'testsu', 'su@example.com', 'testpass')
        self.owner = User.objects.create_user(
            'testowner', 'owner@example.com', 'testpass')
        self.moderator = User.objects.create_user(
            'testmoderator', 'moderator@example.com', 'testpass')
        self.foo_list.add_owner('owner@example.com')
        self.foo_list.add_moderator('moderator@example.com')
        self.mm_user = get_client().create_user('test@example.com', '')
        self.mm_user.addresses[0].verify()
        self.foo_list.subscribe('test@example.com', pre_verified=True,
                                pre_confirmed=True, pre_approved=True)
        self.url = reverse('list_member_options', args=(self.foo_list.list_id,
                                                        'test@example.com',))
        self.url = quote(self.url)

    def test_page_not_accessible_if_not_logged_in(self):
        response = self.client.get(self.url)
        self.assertRedirects(response, '{}?next={}'.format(
            reverse(settings.LOGIN_URL), self.url))

    def test_page_not_accessible_for_unprivileged_users(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_not_accessible_for_moderator(self):
        self.client.login(username='testmoderator', password='testpass')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_page_accessible_for_superuser(self):
        self.client.login(username='testsu', password='testpass')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['moderation_form'],
                              MemberModeration)
        self.assertIsInstance(response.context['preferences_form'],
                              UserPreferences)

    def test_page_accessible_for_owner(self):
        self.client.login(username='testowner', password='testpass')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['moderation_form'],
                              MemberModeration)
        self.assertIsInstance(response.context['preferences_form'],
                              UserPreferences)
