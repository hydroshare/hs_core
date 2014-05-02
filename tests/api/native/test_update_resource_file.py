__author__ = 'Pabitra'

from django.test import TestCase
from django.contrib.auth.models import User
from hs_core import hydroshare
from hs_core.models import GenericResource
from django.core.exceptions import ObjectDoesNotExist
import os
class TestUpdateResourceFileAPI(TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        User.objects.all().delete()
        GenericResource.objects.all().delete()
        pass

    def test_add_resource_files(self):
        # create a user to be used for creating the resource
        user_creator = hydroshare.create_account(
            'creator@usu.edu',
            username='creator',
            first_name='Creator_FirstName',
            last_name='Creator_LastName',
            superuser=False,
            groups=[]
        )

        # create a resource without any owner
        resource = GenericResource.objects.create(
            user=user_creator,
            title='My resource',
            creator=user_creator,
            last_changed_by=user_creator,
            doi='doi1000100010001'
        )

        self.assertEqual(resource.files.all().count(), 0)

        # create a file
        file_original = 'original.txt'

        file_obj = open(file_original, 'w')
        file_obj.write("original text")
        file_obj.close()

        print(file_obj.name)
        file_obj = open(file_original, 'r')
        # add the file to the resource
        added_files = hydroshare.add_resource_files(resource.short_id, file_obj)
        print('Added file count:%d' % len(added_files))

        self.assertEqual(len(added_files), 1)

        # create a file that will be used to update the original file
        file_update = 'update.txt'
        file_obj = open(file_update, 'w')
        file_obj.write("update text")
        file_obj.close()
        file_obj = open(file_update, 'r')

        # FIXME: this api call gives runtime error
        rf = hydroshare.update_resource_file(resource.short_id, file_original, file_obj)

        self.assertEqual(rf.resource_file.name, file_original)

        # since we are updating a file the number of files in the resource needs to be still 1
        self.assertEqual(resource.files.all().count(), 1)

        self.assertIn(
            file_original,
            [os.path.basename(f.resource_file.name) for f in resource.files.all()],
            msg= '%s is not one of the resource files.' % file_original
        )

        # TODO: test the content of the resource file to see if they are the same

        # exception should be raised if we ask to update a file that is not part of the resource
        self.assertRaises(
            ObjectDoesNotExist,
            hydroshare.update_resource_file(resource.short_id, 'badfile.txt', file_obj)
        )

