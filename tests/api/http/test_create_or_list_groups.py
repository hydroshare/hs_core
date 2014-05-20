__author__ = 'shaunjl'
"""
Tastypie REST API tests for CreateOrListGroups.as_view() modeled after: https://github.com/hydroshare/hs_core/blob/master/tests/api/http/test_resource.py

comments- post returns TypeError, put returns HttpResponseForbidden (403)

IMPORTANT- the api calls list_users, but it should call list_groups

"""
from tastypie.test import ResourceTestCase, TestApiClient
from django.contrib.auth.models import Group, User
from hs_core import hydroshare


class CreateOrListGroupsTest(ResourceTestCase):

    def setUp(self):

        self.api_client = TestApiClient()
        
        #create a few groups- 
        owner = hydroshare.create_account(
            'shaun@gmail.com',
            username='user0',
            first_name='User0_FirstName',
            last_name='User0_LastName',
        )
        for num in range(3):
            hydroshare.create_group(name="group{0}".format(num), owners=[owner])


        self.groups_url_base = '/hsapi/groups/'
        
    def tearDown(self):
        Group.objects.all().delete()

    def test_create_group(self):

        post_data= {'name':'newgroup'}

        resp = self.api_client.post(self.groups_url_base, data=post_data ) #returns TypeError:put() takes exactly 2 arguments (1 given)
        resp = self.api_client.put(self.groups_url_base, data=post_data ) #returns HttpResponseForbidden

        self.assertHttpCreated(resp)
        
        grouplist = Group.objects.all() 

        assertTrue(any(Group.objects.filter(name='newgroup'))) 
        assertTrue(len(grouplist)==4)

    def test_list_groups(self):

        query= {
        'owners':'user0' 
        }

        get_data={
        'query': query,
        'status':'',
        'start':'',
        'count':''       
        }

        resp = self.api_client.get(self.group_url_base, data=get_data)
        
        self.assertValidJSONResponse(resp)
        groups = self.deserialize(resp)
            
        for g in groups:
            self.assertEqual(g['owners'], 'user0')
        for num in range(3):
            self.assertIn('group{0}'.format(num),groups.itervalues())

