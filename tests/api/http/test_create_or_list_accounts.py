__author__ = 'shaunjl'
"""
Tastypie REST API tests for CreateOrListAccounts.as_view() modeled after: https://github.com/hydroshare/hs_core/blob/master/tests/api/http/test_resource.py

comments- post returns TypeError, put returns HttpResponseForbidden (403)

"""
from tastypie.test import ResourceTestCase, TestApiClient
from django.contrib.auth.models import User 
from hs_core import hydroshare

class CreateOrListAccountsTest(ResourceTestCase):

    def setUp(self):
        self.account_url_base = '/hsapi/accounts/'

        self.api_client=TestApiClient()
        
    def tearDown(self):
        User.objects.all().delete()

    def test_create_account(self):

        username = 'creator'    
        password = 'password'
        
        post_data = {
            'email': 'shaun@gmail.com',
            'username': username,
            'first_name':'shaun',
            'last_name':'livingston',
            'password': password,
            'superuser': True           
        }

        resp=self.api_client.post(self.account_url_base, data=post_data ) # returns TypeError:put() takes exactly 2 arguments (1 given)
        resp=self.api_client.put(self.account_url_base, data=post_data) # returns HttpResponseForbidden

        self.assertHttpCreated(resp)
        self.assertTrue(User.objects.filter(email='shaun@gmail.com').exists())
        self.assertTrue(User.objects.filter(username=username).exists())
        self.assertTrue(User.objects.filter(first_name='shaun').exists())
        self.assertTrue(User.objects.filter(last_name='livingston').exists())
        self.assertTrue(User.objects.filter(superuser=True).exists())
        
        

    def test_list_users(self):

        user0=hydroshare.create_account(
            'shaun@gmail.com',
            username='user0',
            first_name='User0_FirstName',
            last_name='User0_LastName',
        )

        user1=hydroshare.create_account(
            'shaun@gmail.com',
            username='user1',
            first_name='User1_FirstName',
            last_name='User1_LastName',
        )

        user2=hydroshare.create_account(
            'shaun@gmail.com',
            username='user2',
            first_name='User2_FirstName',
            last_name='User2_LastName',
        )
        
        query= {
        'email':'shaun@gmail.com',
        }

#        query={
#            'from':'auth_user',
#            'select': '*',
#            'where':email='shauntheta@gmail.com'
#            }


        get_data={
        'query': query,
        'status':'',
        'start':'',
        'count':''
        }
        
        resp = self.api_client.get(self.account_url_base, data=get_data)
        self.assertValidJSONResponse(resp)
        for num in range(3):
            self.assertTrue(User.objects.filter(username='user{0}'.format(num)).exists())

        users=self.deserialize(resp)

     #I have no idea if this will work because I don't know what the response looks like, nor how else to test it
        for u in users:
            self.assertEqual(u['email'], 'shaun@gmail.com')
        for num in range(3):
            self.assertIn('user{0}'.format(num), users.itervalues())
        
        
