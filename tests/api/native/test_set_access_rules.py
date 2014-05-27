__author__ = 'lisa stillwell'

from unittest import TestCase
from hs_core.hydroshare import resource
from hs_core.hydroshare import users
from hs_core.models import GenericResource
from django.contrib.auth.models import User
import datetime as dt


class TestSetAccessRules(TestCase):

    def setUp(self):

        # create a user
        self.user1 = users.create_account(
            'lisa@renci.org',
            username='testuser1',
            first_name='Lisa',
            last_name='Stillwell',
            superuser=False,
            groups=[])

        new_res = resource.create_resource(
            'GenericResource',
            self.user1,
            'My Test Resource'
            )

        self.res_id = new_res.short_id

        # get the user's id
        #self.userid = User.objects.get(username=self.user).pk

        #self.group = users.create_group(
            #'MyGroup',
            #members=[self.user],
            #owners=[self.user]
            #)

    def tearDown(self):
        self.user1.delete()
        #self.group.delete()
        #self.res.delete()

    def test_set_access_rules(self):


        # get the resource by pid
        res = resource.get_resource(self.res_id)

