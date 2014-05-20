__author__ = 'shaunjl'
"""
Tastypie REST API tests for GetCapabilities.as_view() modeled after: https://github.com/hydroshare/hs_core/blob/master/tests/api/http/test_resource.py

note- only GET is currently implemented
test_othertypes must be added to in release 3

"""
from django.contrib.auth.models import User
from hs_core import hydroshare
from django.test import TestCase, Client
from hs_core.models import GenericResource
from hs_core.hydroshare.resource import create_resource, get_capabilities


class GetCapabilities(TestCase):
    def setUp(self):
        self.api_client=Client()
        self.user = User.objects.create_user('shaun', 'shauntheta@gmail.com', 'shaun6745')
        self.url = '/hsapi/capabilities/'
        
    def tearDown(self):
        pass

    def test_generic(self):
        res = create_resource('GenericResource',self.user,'res1')
        resp = self.api_client.post(self.url, pk=res.short_id)

        
    def test_othertypes(self):
        pass
        
    
