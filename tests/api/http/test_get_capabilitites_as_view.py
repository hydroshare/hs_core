'''
Unittest for def get_capabilities(pk)

author's notes- 
I think this should be renamed get_extra_capabilities
must be extended to test other types of resources for release 3

'''
__author__='shaunjl'

import unittest
from hs_core import hydroshare
from django.contrib.auth.models import User
from hs_core.models import GenericResource

class TestGetCapabilities(unittest.TestCase):

    def setUp(self): #runs at the beginning of every test
        pass
    def tearDown(self): #runs at the end of every test 

        GenericResource.objects.all().delete()
        User.objects.filter(username='shaun').delete()
        
    def test_generic(self):

        user = User.objects.create_user('shaun', 'shauntheta@gmail.com', 'shaun6745')

        res1 = hydroshare.create_resource('GenericResource',user,'res1')

        extras = hydroshare.get_capabilities(res1.short_id)

        self.assertTrue(extras==None)

     def test_othertypes(self):
         pass
        
 
'''
check def extra_capabilities on hs_core/models.py

useful test assertions-
assertEqual(foo,bar) tests if foo==bar
assertTrue(foo) tests boolean value of any statement you want
assertRaises

see also https://docs.python.org/2.7/library/unittest.html

https://github.com/hydroshare/hs_core/blob/master/hydroshare/resource.py
https://github.com/hydroshare/hs_core/commit/2e2454acf27ac3c39d014dedb18a151263f797c3

'''
