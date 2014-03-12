from django.contrib.auth.models import User

from tastypie.api import Api
from tastypie import fields
from tastypie.authentication import Authentication
from tastypie.authorization import Authorization
from tastypie.resources import ModelResource

from authorization import HydroshareAuthorization
from models import GenericResource
from base64field import Base64FileField

class UserResource(ModelResource):
    class Meta:
        queryset = User.objects.all()
        resource_name = 'user'
        excludes = ['email', 'password', 'is_active', 'is_staff', 'is_superuser']
        authentication = Authentication()
        #authorization = HydroshareAuthorization()
        authorization = Authorization()

class GenericResourceResource(ModelResource):
    resource_file = Base64FileField('resource_file')
    user = fields.ForeignKey(UserResource, 'user')
    creator = fields.ForeignKey(UserResource, 'creator')

    class Meta:
        queryset = GenericResource.objects.all()
        resource_name = 'resource'

        authentication = Authentication()
        #authorization = HydroshareAuthorization()
        authorization = Authorization()
