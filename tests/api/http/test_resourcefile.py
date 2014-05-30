__author__ = 'shaunjl'

"""
Tastypie REST API tests for resourceFileCRUD.as_view

"""
from tastypie.test import ResourceTestCase
from tastypie.test import TestApiClient
from django.contrib.auth.models import User
from hs_core import hydroshare
from tastypie.serializers import Serializer

class ResourceTest(ResourceTestCase):
    serializer= Serializer()
    def setUp(self):
        self.api_client = TestApiClient()

    def tearDown(self):
        User.objects.all().delete()
    def test_resource_file_get(self):  #404 ResponseNotFound- need to give it something other than 'test.txt'
        user = hydroshare.create_account(
            'shaun@gmail.com',
            username='user0',
            first_name='User0_FirstName',
            last_name='User0_LastName',
        )
        n = "test.txt"
        open(n,"w").close()
        myfile = open(n,"r")

        res1 = hydroshare.create_resource('GenericResource', user, 'res1')

        hydroshare.add_resource_files(res1.short_id, myfile)
        url = 'hsapi/resource/{0}/files/{1}/'.format(res1.short_id, 'test.txt')

        resp = self.api_client.get(url)

        self.assertValidJSONResponse(resp)

    def test_resource_file_put(self):
        user = hydroshare.create_account(
            'shaun@gmail.com',
            username='user0',
            first_name='User0_FirstName',
            last_name='User0_LastName',
        )
        n = "test.txt"
        open(n,"w").close()
        myfile = open(n,"r")

        res1 = hydroshare.create_resource('GenericResource', user, 'res1')

        hydroshare.add_resource_files(res1.short_id, myfile)

        n1 = "test1.txt"
        open(n1,"w").close()
        mynewfile = open(n1,"r")

        url = 'hsapi/resource/{0}/files/{1}/'.format(res1.short_id, 'test.txt')

        put_data = self.serialize({'f': 'test1.txt'})

        resp = self.api_client.get(url, data=put_data)

        self.assertHttpAccepted(resp)

    def test_resource_file_post(self):
        user = hydroshare.create_account(
            'shaun@gmail.com',
            username='user0',
            first_name='User0_FirstName',
            last_name='User0_LastName',
        )
        n = "test.txt"
        open(n,"w").close()
        myfile = open(n,"r")

        res1 = hydroshare.create_resource('GenericResource', user, 'res1')

        url = 'hsapi/resource/{0}/files/{1}/'.format(res1.short_id, 'test.txt')

        resp = self.api_client.get(url)

    def test_resource_file_delete(self):

        user = hydroshare.create_account(
            'shaun@gmail.com',
            username='user0',
            first_name='User0_FirstName',
            last_name='User0_LastName',
        )
        n = "test.txt"
        open(n,"w").close()
        myfile = open(n,"r")

        res1 = hydroshare.create_resource('GenericResource', user, 'res1')

        hydroshare.add_resource_files(res1.short_id, myfile)
        url = 'hsapi/resource/{0}/files/{1}/'.format(res1.short_id, 'test.txt')

        resp = self.api_client.delete(url)

        self.assertValidJSONResponse(resp)
