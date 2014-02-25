from django.contrib.auth.models import User

from tastypie.authorization import Authorization
from tastypie.resources import ModelResource
from tastypie.api import Api

from models import GenericResource


class UserResource(ModelResource):
    class Meta:
        queryset = User.objects.all()
        resource_name = 'user'
        excludes = ['email', 'password', 'is_active', 'is_staff', 'is_superuser']

class GenericResourceResource(ModelResource):
    class Meta:
        queryset = GenericResource.objects.all()
        resource_name = 'resource'
        authorization = Authorization()

