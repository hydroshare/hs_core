from django.conf.urls import patterns, url
from . import views

urlpatterns = patterns('',

    # users API

    url(r'^resource/owner/(?P<pk>[A-z0-9]+)/$', views.SetResourceOwner.as_view()),
    url(r'^resource/accessRules/(?P<pk>[A-z0-9]+)/$', views.SetAccessRules.as_view()),
    url(r'^accounts/$', views.CreateOrListAccounts.as_view()),
    url(r'^accounts/(?P<pk>[A-z0-9]+)/$', views.UpdateAccountOrUserInfo.as_view()),
    url(r'^groups/$', views.CreateOrListGroups.as_view()),
    url(r'^groups/(?P<pk>[A-z0-9]+)/$', views.ListGroupMembers.as_view()),
    url(r'^groups/(?P<g>[A-z0-9]+)/owner/(?P<u>[A-z0-9]+)/$', views.SetOrDeleteGroupOwner.as_view()),
    url(r'^resources/$', views.GetResourceList.as_view()),

    # resource API

    url(r'^resource/$', views.ResourceCRUD.as_view()),
    url(r'^resource/(?P<pk>[A-z0-9]+)/$', views.ResourceCRUD.as_view()),
    url(r'^resource/(?P<pk>[A-z0-9]+)/files/$', views.ResourceFileCRUD.as_view()),
    url(r'^resource/(?P<pk>[A-z0-9]+)/files/(?P<filename>[^/]+)/$', views.ResourceFileCRUD.as_view()),
    url(r'^scimeta/(?P<pk>[A-z0-9]+)/$', views.GetUpdateScienceMetadata.as_view()),
    url(r'^sysmeta/(?P<pk>[A-z0-9]+)/$', views.GetUpdateSystemMetadata.as_view()),
    url(r'^capabilities/(?P<pk>[A-z0-9]+)/$', views.GetCapabilities.as_view()),
    url(r'^revisions/(?P<pk>[A-z0-9]+)/$', views.GetRevisions.as_view()),
    url(r'^related/(?P<pk>[A-z0-9]+)/$', views.GetRelated.as_view()), # raises not implemented
    url(r'^checksum/(?P<pk>[A-z0-9]+)/$', views.GetChecksum.as_view()), # raises not implemented
    url(r'^publishResource/(?P<pk>[A-z0-9]+)/$', views.PublishResource.as_view()), # raises not implemented
    url(r'^resolveDOI/(?P<doi>[A-z0-9]+)/$', views.ResolveDOI.as_view()), # raises not implemented

    # internal API

    url(r'^_internal/add_file_to_resource/(?P<shortkey>[A-z0-9]+)/$', views.add_file_to_resource),
)

