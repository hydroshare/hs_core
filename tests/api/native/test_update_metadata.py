__author__ = 'shaunjl'
"""
Tastypie API tests for update_science_metadata and update_system_metadata

comments-

"""
from tastypie.test import ResourceTestCase, TestApiClient
from django.contrib.auth.models import User, Group
from hs_core import hydroshare
from dublincore.models import QualifiedDublinCoreElement as QDCE
from mezzanine.generic.models import Keyword, AssignedKeyword


class UpdateMetadataTest(ResourceTestCase):
    def setUp(self):
        user = hydroshare.create_account(
            'shaun@gmail.com',
            username='shaunjl',
            first_name='shaun',
            last_name='john',
            superuser=True,
            )
        self.res = hydroshare.create_resource('GenericResource',user,'res')
    def tearDown(self):
        User.objects.all().delete()
        hydroshare.delete_resource(self.res.short_id)
        QDCE.objects.all().delete()
        Keyword.objects.all().delete()
        #AssignedKeyword.objects.all().delete()

    def test_update_science_metadata(self):
        d_m = [{
            'term':'SRC',
            'qualifier': 'BYU Archives',
            'content': 'Archive may be found at HBLL Library at HBLL:S102948'
            },
            {
            'term':'REP',
            'qualifier': "Dr. Nielson's work",
            'content': 'replaced in 2003'
            },
            {
            'term':'PBL',
            'qualifier': 'Dr. Ames',
            'content': 'Published 2001'
            }]

        hydroshare.update_science_metadata(self.res.short_id, dublin_metadata=d_m)

        for t in ('SRC','REP', 'PBL')
            self.assertTrue(any(QDCE.objects.filter(term=t)))
        self.assertEqual(QDCE.objects.all(), QDCE.objects.filter(content_object=res))



    def test_update_keywords(self):
        kws= ['kw1','kw2','kw3']

        hydroshare.update_system_metadata(self.res.short_id, keywords=kws)

        self.assertEqual(AssignedKeyword.objects.filter(object_pk=res.id),Keyword.objects.all())

    def test_update_kwargs(self):
        kwargs = {'description':'new description',
                  'title':'new title'
                  }

        hydroshare.update_system_metadata(self.res.short_id, **kwargs)

        self.assertEqual(res.description,'new description')
        self.assertEqual(user.title,'new title')




