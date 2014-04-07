from django.conf.urls import patterns, url
from . import views

urlpatterns = patterns('',
    url(r'^resource/owner/(?P<pk>[A-z0-9]+)/$', views.SetResourceOwner.as_view()),
    url(r'^resource/accessRules/(?P<pk>[A-z0-9]+)/$', views.SetAccessRules.as_view()),

    # internal API

    url(r'^_internal/add_file_to_resource/(?P<shortkey>[A-z0-9]+)/$', views.add_file_to_resource),
)

