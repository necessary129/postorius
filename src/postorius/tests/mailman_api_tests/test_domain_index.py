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

import logging

from django.core.urlresolvers import reverse
from django.test import Client, TestCase
from django.contrib.auth.models import User
try:
    from urllib2 import HTTPError
except ImportError:
    from urllib.error import HTTPError

from postorius.utils import get_client
from postorius.tests import MM_VCR


logger = logging.getLogger(__name__)
vcr_log = logging.getLogger('vcr')
vcr_log.setLevel(logging.WARNING)


class DomainIndexPageTest(TestCase):
    """Tests for the list index page."""

    @MM_VCR.use_cassette('test_domain_index.yaml')
    def setUp(self):
        self.domain = get_client().create_domain('example.com')
        try:
            self.foo_list = self.domain.create_list('foo')
        except HTTPError:
            self.foo_list = get_client().get_list('foo.example.com')

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

    @MM_VCR.use_cassette('test_domain_index.yaml')
    def tearDown(self):
        self.foo_list.delete()
        self.user.delete()
        self.superuser.delete()
        self.owner.delete()
        self.moderator.delete()
        get_client().delete_domain('example.com')

    @MM_VCR.use_cassette('test_domain_index.yaml')
    def test_domain_index_not_accessible_to_public(self):
        # The list index page should contain the lists
        response = self.client.get(reverse('domain_index'))
        self.assertEqual(response.status_code, 302)

    @MM_VCR.use_cassette('test_domain_index.yaml')
    def test_domain_index_not_accessible_to_unpriveleged_user(self):
        # The list index page should contain the lists
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('domain_index'))
        self.assertEqual(response.status_code, 302)

    @MM_VCR.use_cassette('test_domain_index.yaml')
    def test_domain_index_not_accessible_to_moderators(self):
        # The list index page should contain the lists
        self.client.login(username='testmoderator', password='testpass')
        response = self.client.get(reverse('domain_index'))
        self.assertEqual(response.status_code, 302)

    @MM_VCR.use_cassette('test_domain_index.yaml')
    def test_domain_index_not_accessible_to_owners(self):
        # The list index page should contain the lists
        self.client.login(username='testowner', password='testpass')
        response = self.client.get(reverse('domain_index'))
        self.assertEqual(response.status_code, 302)

    @MM_VCR.use_cassette('test_domain_index.yaml')
    def test_domain_index_contains_the_domains(self):
        # The list index page should contain the lists
        self.client.login(username='testsu', password='testpass')
        response = self.client.get(reverse('domain_index'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['domains']), 1)
        self.assertContains(response, 'example.com')
