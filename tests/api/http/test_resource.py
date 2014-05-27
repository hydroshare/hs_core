__author__ = 'selimnairb@gmail.com'
"""
Tastypie REST API tests for resources modeled after: http://django-tastypie.readthedocs.org/en/latest/testing.html

"""
from tastypie.test import ResourceTestCase
from tastypie.test import TestApiClient

from django.contrib.auth.models import User
from hs_core import hydroshare
from hs_core.models import GenericResource

class ResourceTest(ResourceTestCase):

    def setUp(self):
        self.api_client = TestApiClient()

        self.username = 'creator'
        self.password = 'mybadpassword'

        # create a user to be used for creating the resource
        self.user_creator = hydroshare.create_account(
            'creator@hydroshare.org',
            username=self.username,
            first_name='Creator_FirstName',
            last_name='Creator_LastName',
            superuser=False,
            password=self.password,
            groups=[]
        )
        self.user_url = '/hsapi/accounts/{0}/'.format(self.user_creator.username)

        # create a resource without any owner
        self.resource = GenericResource.objects.create(
            user=self.user_creator,
            title='My resource',
            creator=self.user_creator,
            last_changed_by=self.user_creator,
            doi='doi1000100010001'
        )
        self.resource_url_base = '/hsapi/resource'
        self.resource_url = '{0}/{1}/'.format(self.resource_url_base, self.resource.short_id)

        self.post_data = {
            'user': self.user_url,
            'title': 'My REST API-created resource',
            'creator': self.user_url,
            'last_changed_by': self.user_url,
            'doi': 'doi1000100010002'
        }

    def tearDown(self):
        User.objects.all().delete()
        GenericResource.objects.all().delete()

    def get_credentials(self):
        return self.create_basic(username=self.username, password=self.password)

    def test_resource_get(self):
        resp = self.api_client.get(self.resource_url, format='json',
                                   authentication=self.get_credentials() )
        self.assertValidJSONResponse(resp)

        resource = self.deserialize(resp)
        self.assertEqual( self.resource.short_id, resource.short_id )
        self.assertEqual( self.resource.user, resource.user )
        self.assertEqual( self.resource.title, resource.title )
        self.assertEqual( self.resource.doi, resource.doi )

    def test_resource_post(self):
        resp = self.api_client.post(self.resource_url_base, format='json', data=self.post_data,
                                    authentication=self.get_credentials() )
        self.assertHttpCreated(resp)

        pid = self.deserialize(resp) # Not sure how the PID will be encoded, assuming it is just a string
        new_resource_url = '{0}/{1}/'.format(self.resource_url_base, pid)

        resp = self.api_client.get(new_resource_url, format='json')
        self.assertValidJSONResponse(resp)

        resource = self.deserialize(resp)
        self.assertEqual( pid, resource.short_id )
        self.assertEqual( self.post_data['user'], resource.user )
        self.assertEqual( self.post_data['title'], resource.title )
        self.assertEqual( self.post_data['doi'], resource.doi )

    def test_resource_put(self):
        resp = self.api_client.get(self.resource_url, format='json',
                                   authentication=self.get_credentials() )
        self.assertValidJSONResponse(resp)

        original_data = self.deserialize(resp)
        new_data = original_data.copy()
        new_data['title'] = 'My UPDATED REST API-created resource'

        self.assertHttpAccepted( self.api_client.put(self.resource_url, format='json', data=new_data,
                                                     authentication=self.get_credentials() ))

        updated_data = self.deserialize(self.api_client.get(self.resource_url, format='json'),
                                        authentication=self.get_credentials() )
        self.assertEquals( new_data['title'], updated_data['title'] )

    def test_resource_delete(self):
        x = self.api_client.delete(self.resource_url, format='json',  authentication=self.get_credentials() )
        self.assertIn(x.status_code, [202, 204, 301])
        self.assertHttpNotFound( self.api_client.get(self.resource_url, format='json',
                                                     authentication=self.get_credentials() ))
