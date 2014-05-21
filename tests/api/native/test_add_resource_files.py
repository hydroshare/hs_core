import unittest
from hs_core.hydroshare.resource import add_resource_files, create_resource
from hs_core.models import GenericResource
from django.contrib.auth.models import User
from hs_core.models import ResourceFile


class testAddResourceFiles(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        User.objects.filter(username='shaun').delete() #delete user after test is done

    def test_add_files(self):
        user = User.objects.create_user('shaun', 'shauntheta@gmail.com', 'shaun6745') #create user

        #create files
        n1 = "test.txt"
        n2 = "test2.txt"
        n3 = "test3.txt"

        myfile = open(n1,"w") #files are created
        myfile1 = open(n2,"w")
        myfile2 = open(n3,"w")

        myfile = open(n1,"r") #files are opened as 'read-only'
        myfile1 = open(n2,"r")
        myfile2 = open(n3,"r")

        res1 = create_resource('GenericResource',user,'res1') #create resource

        #delete all resource files for created resource
        for f in ResourceFile.objects.filter(object_id=res1.pk):
            f.resource_file.delete()

        #add files
        add_resource_files(res1.short_id,myfile,myfile1,myfile2)

        #add each file of resource to list
        l=[]
        for f in ResourceFile.objects.filter(object_id=res1.pk):
            l.append(f.resource_file.name)

        #check if the file name is in the list of files
        self.assertTrue(res1.short_id+"/"+n1 in l, "file 1 has not been added")
        self.assertTrue(res1.short_id+"/"+n2 in l, "file 2 has not been added")
        self.assertTrue(res1.short_id+"/"+n3 in l, "file 3 has not been added")

        
