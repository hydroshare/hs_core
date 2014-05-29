from __future__ import absolute_import

from django.db.models import get_model, get_models
from django.http import Http404
from django.shortcuts import get_object_or_404
from hs_core.models import AbstractResource
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User, Group
from . import hs_bagit
import importlib

cached_resource_types = None

def get_resource_types():
    global cached_resource_types
    cached_resource_types = filter(lambda x: issubclass(x, AbstractResource), get_models()) if\
        not cached_resource_types else cached_resource_types

    return cached_resource_types


def get_resource_instance(app, model_name, pk, or_404=True):
    model = get_model(app, model_name)
    if or_404:
        return get_object_or_404(model, pk=pk)
    else:
        return model.objects.get(pk=pk)


def get_resource_by_shortkey(shortkey, or_404=True):
    models = get_resource_types()
    for model in models:
        m = model.objects.filter(short_id=shortkey)
        if m.exists():
            return m[0]
    if or_404:
        raise Http404(shortkey)
    else:
        raise ObjectDoesNotExist(shortkey)


def get_resource_by_doi(doi, or_404=True):
    models = get_resource_types()
    for model in models:
        m = model.objects.filter(doi=doi)
        if m.exists():
            return m[0]
    if or_404:
        raise Http404(doi)
    else:
        raise ObjectDoesNotExist(doi)


def user_from_id(user):
    if isinstance(user, User):
        return user

    try:
        tgt = User.objects.get(username=user)
    except ObjectDoesNotExist:
        try:
            tgt = User.objects.get(email=user)
        except ObjectDoesNotExist:
            try:
                tgt = User.objects.get(pk=int(user))
            except ValueError:
                raise Http404('User not found')
            except ObjectDoesNotExist:
                raise Http404('User not found')
    return tgt


def group_from_id(grp):
    if isinstance(grp, Group):
        return grp

    try:
        tgt = Group.objects.get(name=grp)
    except ObjectDoesNotExist:
        try:
            tgt = Group.objects.get(pk=int(grp))
        except TypeError:
            raise Http404('Group not found')
        except ObjectDoesNotExist:
            raise Http404('Group not found')
    return tgt


def serialize_science_metadata(res):
    serializer = get_serializer(res)
    bundle = serializer.build_bundle(obj=res)
    return serializer.serialize(None, serializer.full_dehydrate(bundle), 'application/json')


def serialize_system_metadata(res):
    serializer = get_serializer(res)
    bundle = serializer.build_bundle(obj=res)
    return serializer.serialize(None, serializer.full_dehydrate(bundle), 'application/json')


def serialize_resource_map(res):
    serializer = get_serializer(res)
    bundle = serializer.build_bundle(obj=res)
    return serializer.serialize(None, serializer.full_dehydrate(bundle), 'application/json')


def get_serializer(resource):
    tastypie_module = resource._meta.app_label + '.api'        # the module name should follow this convention
    tastypie_name = resource._meta.object_name + 'Resource'    # the classname of the Resource seralizer
    tastypie_api = importlib.import_module(tastypie_module)    # import the module
    return getattr(tastypie_api, tastypie_name)()        # make an instance of the tastypie resource


def resource_modified(resource, by_user=None):
    resource.last_changed_by = by_user
    resource.save()
    hs_bagit.create_bag(resource)