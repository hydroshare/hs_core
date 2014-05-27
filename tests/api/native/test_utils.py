from unittest import TestCase
from hs_core.hydroshare import utils
from hs_core.models import GenericResource
from django.contrib.auth.models import Group, User

class TestUtils(TestCase):
    def setUp(self):
        try:
            self.user = User.objects.create_user('user1', email='user1@nowhere.com')
        except:
            self.tearDown()
            self.user = User.objects.create_user('user1', email='user1@nowhere.com')

        self.group, _ = Group.objects.get_or_create(name='group1')
        self.res, created = GenericResource.objects.get_or_create(
            user=self.user,
            title='resource',
            creator=self.user,
            last_changed_by=self.user,
            doi='doi1000100010001'
        )
        if created:
            self.res.owners.add(self.user)

    def tearDown(self):
        User.objects.all().delete()
        Group.objects.all().delete()
        GenericResource.objects.all().delete()

    def test_get_resource_types(self):
        # first time gets them anew
        self.assertListEqual(
            [GenericResource],
            utils.get_resource_types(),
            msg="Resource types was more than just [GenericResource]")

        # second time gets cached instances
        self.assertListEqual(
            [GenericResource],
            utils.get_resource_types(),
            msg="Resource types was more than just [GenericResource] using cached resource types")

    def test_get_resource_instance(self):
        self.assertEqual(
            utils.get_resource_instance('hs_core', 'GenericResource', self.res.pk),
            self.res
        )

    def test_get_resource_by_shortkey(self):
        self.assertEqual(
            utils.get_resource_by_shortkey(self.res.short_id),
            self.res
        )

    def test_get_resource_by_doi(self):
        self.assertEqual(
            utils.get_resource_by_doi('doi1000100010001'),
            self.res
        )

    def test_user_from_id(self):
        self.assertEqual(
            utils.user_from_id(self.user),
            self.user,
            msg='user passthrough failed'
        )

        self.assertEqual(
            utils.user_from_id('user1@nowhere.com'),
            self.user,
            msg='lookup by email address failed'
        )

        self.assertEqual(
            utils.user_from_id('user1'),
            self.user,
            msg='lookup by username failed'
        )

    def test_group_from_id(self):
        self.assertEqual(
            utils.group_from_id(self.group),
            self.group,
            msg='group passthrough failed'
        )

        self.assertEqual(
            utils.group_from_id('group1'),
            self.group,
            msg='lookup by group name failed'
        )

