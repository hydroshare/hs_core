__author__ = 'tonycastronova'

from unittest import TestCase
from hs_core.hydroshare import resource
from hs_core.hydroshare import users
from hs_core.models import GenericResource
from django.contrib.auth.models import User
import datetime as dt


class TestCreateResource(TestCase):

    def setUp(self):

        # create a user
        self.user = users.create_account(
            'test_user@email.com',
            username='testuser',
            first_name='some_first_namne',
            last_name='some_last_name',
            superuser=False,
            groups=[])

        # get the user's id
        self.userid = User.objects.get(username=self.user).pk

        self.group = users.create_group(
            'MyGroup',
            members=[self.user],
            owners=[self.user]
            )

    def tearDown(self):
        self.user.delete()
        self.group.delete()
        #self.res.delete()

    def test_create_resource(self):


        new_res = resource.create_resource(
            'GenericResource',
            self.user,
            'My Test Resource'
            )



        pid = new_res.short_id

        # get the resource by pid
        res = resource.get_resource(pid)

        self.assertTrue(res is not None)
        self.assertTrue(type(res) == GenericResource, type(res))
        self.assertTrue(res.title == 'My Test Resource')
        self.assertTrue(res.created.strftime('%m/%d/%Y %H:%M') == res.updated.strftime('%m/%d/%Y %H:%M') )
        self.assertTrue(res.created.strftime('%m/%d/%Y') == dt.datetime.today().strftime('%m/%d/%Y'))
        self.assertTrue(res.creator_id == self.userid)
        self.assertTrue(res.short_id is not None, 'Short ID has not been created!')
        self.assertTrue(res.short_url is not None, 'Short URL has not been created!')
        self.assertTrue(res.bagit is not None, 'Bagithas not been created!')



