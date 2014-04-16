from __future__ import absolute_import

from django import forms
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from hs_core import hydroshare
from hs_core.api import UserResource, GroupResource
from hs_core.hydroshare.utils import group_from_id, user_from_id
from .utils import authorize
from django.views.generic import View


class SetAccessRules(View):
    class SetAccessRulesForm(forms.Form):
        pid = forms.CharField(max_length=32, min_length=1)
        principalType = forms.ChoiceField(choices=(('user','user'), ('group','group')))
        principalID = forms.CharField(max_length=128, min_length=1)
        access = forms.ChoiceField(choices=(('edit','edit'), ('view', 'view')))
        allow = forms.BooleanField()

    class SetDoNotDistributeForm(forms.Form):
        pid = forms.CharField(max_length=32, min_length=1)
        access = forms.ChoiceField(choices=(('donotdistribute','donotdistribute'),('public','public')))
        allow = forms.BooleanField()

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        super(SetAccessRules, self).dispatch(request, *args, **kwargs)

    def get(self, pk):
        ur = UserResource()
        gr = GroupResource()

    def post(self, pk):
        self.put(pk)

    def put(self, pk):
        self.set_access_rules(self.request, pk)

    def set_access_rules(self, request, pk):
        """
        Set the access permissions for an object identified by pid. Triggers a change in the system metadata. Successful
        completion of this operation in indicated by a HTTP response of 200. Unsuccessful completion of this operation must
        be indicated by returning an appropriate exception such as NotAuthorized.

        REST URL:  PUT /resource/accessRules/{pid}/?principaltype=({userID}|{groupID})&principleID={id}&access=(edit|view|donotdistribute)&allow=(true|false)

        Parameters:
        pid - Unique HydroShare identifier for the resource to be modified
        principalType - The type of principal (user or group)
        principalID - Identifier for the user or group to be granted access
        access - Permission to be assigned to the resource for the principal
        allow - True for granting the permission, False to revoke

        Returns: The pid of the resource that was modified

        Return Type: pid

        Raises:
        Exceptions.NotAuthorized - The user is not authorized
        Exceptions.NotFound - The resource identified by pid does not exist
        Exceptions.NotFound - The principal identified by principalID does not exist
        Exception.ServiceFailure - The service is unable to process the request

        Note:  Do not distribute is an attribute of the resource that is set by a user with Full permissions and only
        applies to users with Edit and View privileges. There is no share privilege in HydroShare. Share permission is
        implicit unless prohibited by the Do not distribute attribute. The only permissions in HydroShare are View, Edit and
        Full.

        As-built notes:  The API had no way to declare a resource publicly viewable, this has been added.
        access parameter can be 'public'.  Using allow=true, that will cause the resource to become publicly viewable

        """
        res, _, _ = authorize(request, pk, full=True, superuser=True)

        access_rules_form = SetAccessRules.SetAccessRulesForm(request.REQUEST)
        if access_rules_form.is_valid():
            r = access_rules_form.cleaned_data

            # get the user or group by ID
            # try username first, then email address, then primary key
            if r['principalType'] == 'user':
                tgt = user_from_id(r['principalID'])
                ret = hydroshare.set_access_rules(user=tgt, pk=res, access=r['access'], allow=r['allow'])
            else:
                tgt = group_from_id(r['principalID'])
                ret = hydroshare.set_access_rules(group=tgt, pk=res, access=r['access'], allow=r['allow'])
        else:
            distribute_form = SetAccessRules.SetDoNotDistributeForm(request.REQUEST)
            if distribute_form.is_valid():
                r = distribute_form.cleaned_data
                ret = hydroshare.set_access_rules(pk=res, access=r['access'], allow=r['allow'])
            else:
                raise TypeError('Invalid request')

        return HttpResponse(ret, content_type='text/plain')



class SetResourceOwner(View):
    class SetResourceOwnerForm(forms.Form):
        user = forms.CharField(min_length=1)

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        super(SetResourceOwner, self).dispatch(request, *args, **kwargs)

    def get(self, pk):
        raise NotImplemented()

    def post(self, pk):
        self.put(pk)

    def put(self, pk):
        self.set_resource_owner(self.request, pk)

    def set_resource_owner(self, request, pk):
        """
        Changes ownership of the specified resource to the user specified by a userID.

        REST URL:  PUT /resource/owner/{pid}?user={userID}

        Parameters:
        pid - Unique HydroShare identifier for the resource to be modified
        userID - ID for the user to be set as an owner of the resource identified by pid

        Returns: The pid of the resource that was modified

        Return Type: pid

        Raises:
        Exceptions.NotAuthorized - The user is not authorized
        Exceptions.NotFound - The resource identified by pid does not exist
        Exception.ServiceFailure - The service is unable to process the request
        Note:  This can only be done by the resource owner or a HydroShare administrator.

        """
        res, _, _ = authorize(request, pk, full=True, superuser=True)
        params = SetResourceOwner.SetResourceOwnerForm(request.REQUEST)
        if params.is_valid():
            r = params.cleaned_data
            tgt = user_from_id(r['user'])
            return hydroshare.set_resource_owner(pk=res, user=tgt)



