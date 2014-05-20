__author__ = 'shaunjl'
"""
Tastypie REST API tests for CreateOrListGroups.as_view() modeled after: https://github.com/hydroshare/hs_core/blob/master/tests/api/http/test_resource.py

comments- post returns TypeError, put returns HttpResponseForbidden (403)

IMPORTANT- the api calls list_users, but it should call list_groups

"""
from tastypie.test import ResourceTestCase, TestApiClient
from tastypie.serializers import Serializer
from django.contrib.auth.models import Group, User
from hs_core import hydroshare


class CreateOrListGroupsTest(ResourceTestCase):
    serializer = Serializer()
    def setUp(self):

        self.api_client = TestApiClient()

        user = hydroshare.create_account(
            'shaun@gmail.com',
            username='user0',
            first_name='User0_FirstName',
            last_name='User0_LastName',
        )

        g0=hydroshare.create_group(name="group0")
        g1=hydroshare.create_group(name="group1")
        g2=hydroshare.create_group(name="group2")
        user.groups.add(g0,g1,g2)
        self.g_ids=[g0.id,g1.id,g2.id]
            
        self.groups_url_base = '/hsapi/groups/'
        
    def tearDown(self):
        Group.objects.all().delete()
        User.objects.all().delete()

    def test_create_group(self):

        post_data = {'name': 'newgroup'}

        try:
            resp = self.api_client.post(self.groups_url_base, data=post_data)  
        # returns TypeError:put() takes exactly 2 arguments (1 given)
        except:
            resp = self.api_client.put(self.groups_url_base, data=post_data)   
        # returns HttpResponseForbidden

        self.assertHttpCreated(resp)
        
        grouplist = Group.objects.all() 
        num_of_groups=len(grouplist)
        
        assertTrue(any(Group.objects.filter(name='newgroup'))) 
        assertTrue(num_of_groups==4)

    def test_list_groups(self):

        query = self.serialize({'user': 'user0'})

        get_data = {'query': query }

        resp = self.api_client.get(self.groups_url_base, data=get_data)
        print resp
        self.assertEqual(resp.status_code,200)

        groups = self.deserialize(resp)

        new_ids=[]
        for num in len(groups):
            new_ids.append(groups[num]['id'])
            self.assertEqual(str(groups[num]['user']), 'user0')
            self.assertEqual(str(groups[num]['name']), 'group{0}'.format(num))
        assertEqual(sorted(self.g_ids,sorted(new_ids))




