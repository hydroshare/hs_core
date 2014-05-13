__author__ = 'shaunjl'
"""
Tastypie REST API tests for CreateOrListAccounts modeled after: https://github.com/hydroshare/hs_core/blob/master/tests/api/http/test_resource.py

"""
from tastypie.test import ResourceTestCase
from tastypie.test import TestApiClient
from django.contrib.auth.models import User
from hs_core import hydroshare


class ResourceTest(ResourceTestCase):

    def setUp(self):
        self.api_client = TestApiClient()

        self.username = 'creator'
        self.password = 'password'

        # manually create a user to be used for comparison with user created in POST and received in GET
        self.manual_user = hydroshare.create_account(
            'shauntheta@gmail.com',
            username=self.username,
            first_name='User_FirstName',
            last_name='User_LastName',
            superuser=True,
        ) 

        self.account_url_base = '/hsapi/accounts'
        self.account_url = '/{0}/{1}/'.format(self.account_url_base, self.manual_user.id) 

        # create data for POST that matches the manual_user
        self.post_data = {
            'email': 'shauntheta@gmail.com',
            'username': self.username,
            'superuser': True           
        }
        
    def tearDown(self):
        User.objects.all().delete() 

    def get_credentials(self):
        return self.create_basic( username=self.username, password=self.password )

    def test_create_account(self):
        # submitting POST request, with response type json
        resp = self.api_client.post(self.account_url_base, format='json', data=self.post_data,
                                    authentication=self.get_credentials() ) #maybe not base as URI

        self.assertHttpCreated(resp)

        # deserialize takes an HTTPResponse and returns a datastructure (usually a dictionary) 
        usr_name = self.deserialize(resp) # Not sure how the PID will be encoded, assuming it is just a string
        new_account_url = '{0}/{1}/'.format(self.account_url_base, usr_name )

        # submitting GET request, response type json
        resp = self.api_client.get(new_account_url, format='json' )
        self.assertValidJSONResponse(resp)

        # deserialize takes an HTTPResponse and returns a datastructure (usually a dictionary) 
        account = self.deserialize(resp)
        
        self.assertEqual( self.post_data['email'], account.email )
        self.assertEqual( self.post_data['username'], account.username )

    def test_list_users(self): #need to add multiple users 
        resp = self.api_client.get(self.account_url, format='json',
                                   authentication=self.get_credentials() )
        self.assertValidJSONResponse(resp)

        account = self.deserialize(resp)
        
        self.assertEqual( self.manual_user.username, account.username )
        self.assertEqual( self.manual_user.email, account.email )


