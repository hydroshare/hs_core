__author__ = 'shaunjl'
"""
Tastypie REST API tests for SetResourceOwner.as_view

comments- set owner test gives 403

"""
from django.contrib.auth.models import User
from hs_core import hydroshare
from tastypie.test import ResourceTestCase, TestApiClient
from tastypie.serializers import Serializer
from hs_core.models import GenericResource

class SetResourceOwnerTest(ResourceTestCase):
    serializer = Serializer()
    def setUp(self):
        self.api_client=TestApiClient()
        self.user = hydroshare.create_account(
            'shaun@gmail.com',
            username='user',
            first_name='User_FirstName',
            last_name='User_LastName',
            )
        self.url_base = '/hsapi/resource/owner/'

    def tearDown(self):
        User.objects.all().delete()

    def test_set_owner(self):
        res = hydroshare.create_resource('GenericResource', self.user, 'res1')
        user2 = hydroshare.create_account(
            'shaun@gmail.com',
            username='user2',
            first_name='User2_FirstName',
            last_name='User2_LastName',
            )
        post_data={'user': user2.id}
        url='{0}{1}/'.format(self.url_base,res.short_id)
        resp = self.api_client.put(url, data=post_data)

        self.assertValidJSONResponse(resp)

        rtrned_res = self.deserialize(resp) #returned_resource

        self.assertEqual(res.short_id, rtrned_res['short_id'])

        hydroshare.delete_resource(res.short_id)