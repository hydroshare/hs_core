from django.contrib.auth.models import User

from tastypie.api import Api
from tastypie import fields
from tastypie.authentication import BasicAuthentication
from tastypie.authorization import Authorization
from tastypie.resources import ModelResource
from tastypie.constants import ALL

from authorization import HydroshareAuthorization
from models import GenericResource
from base64field import Base64FileField

class UserResource(ModelResource):
    class Meta:
        always_return_data = True
        queryset = User.objects.all()
        resource_name = 'user'
        excludes = ['email', 'password', 'is_active', 'is_staff', 'is_superuser']
        filtering = {
            'username': ALL,
        }
        authentication = BasicAuthentication()
        #authorization = HydroshareAuthorization()
        authorization = Authorization()

class GenericResourceResource(ModelResource):
    resource_file = Base64FileField('resource_file')
    user = fields.ForeignKey(UserResource, 'user')
    creator = fields.ForeignKey(UserResource, 'creator')

    class Meta:
        always_return_data = True
        queryset = GenericResource.objects.all()
        resource_name = 'resource'
        filtering = {
            'id': 'exact',
        }
        authentication = BasicAuthentication()
        #authorization = HydroshareAuthorization()
        authorization = Authorization()
