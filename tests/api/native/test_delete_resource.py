from django.http import Http404

__author__ = 'tonycastronova'

from unittest import TestCase
from hs_core.hydroshare import resource
from hs_core.hydroshare import users
from hs_core.models import GenericResource
from django.contrib.auth.models import User
import datetime as dt


class TestGetResource(TestCase):

    def setUp(self):

        # create a user
        self.user = users.create_account(
            'test_user@email.com',
            username='testuser',
            first_name='some_first_name',
            last_name='some_last_name',
            superuser=False,
            groups=[])

        # get the user's id
        self.userid = User.objects.get(username=self.user).pk

        self.group = users.create_group(
            'MytestGroup1',
            members=[self.user],
            owners=[self.user]
            )

        new_res = resource.create_resource(
            'GenericResource',
            self.user,
            'My Test Resource'
            )
        self.pid = new_res.short_id

    def tearDown(self):
        self.user.delete()
        self.group.delete()

    def test_delete_resource(self):

        # get the resource by pid
        res = resource.get_resource(self.pid)
        self.assertTrue(res is not None)

        # delete the resource
        resource.delete_resource(self.pid)

        # try to get the resource again
        self.assertRaises(resource.get_resource(self.pid), Http404)




