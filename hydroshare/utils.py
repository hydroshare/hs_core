from django.db.models import get_model, get_models
from django.http import Http404
from django.shortcuts import get_object_or_404
from hs_core.models import AbstractResource
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User, Group

def get_resource_instance(app, model_name, pk, or_404=True):
    model = get_model(app, model_name)
    if or_404:
        get_object_or_404(model, pk=pk)
    else:
        model.objects.get(pk=pk)

def get_resource_by_shortkey(shortkey, or_404=True):
    models = filter(lambda x: issubclass(x, AbstractResource), get_models())
    for model in models:
        m = model.objects.filter(short_id=shortkey)
        if m.exists():
            return m[0]
    if or_404:
        raise Http404(shortkey)
    else:
        raise ObjectDoesNotExist(shortkey)

def get_resource_by_doi(doi, or_404=True):
    models = filter(lambda x: issubclass(x, AbstractResource), get_models())
    for model in models:
        m = model.objects.filter(doi=doi)
        if m.exists():
            return m[0]
    if or_404:
        raise Http404(doi)
    else:
        raise ObjectDoesNotExist(doi)

def user_from_id(user):
    try:
        tgt = User.objects.get(username=user)
    except ObjectDoesNotExist:
        try:
            tgt = User.objects.get(email=user)
        except ObjectDoesNotExist:
            try:
                tgt = User.objects.get(pk=int(user))
            except TypeError:
                raise Http404('User not found')
            except ObjectDoesNotExist:
                raise Http404('User not found')
    return tgt

def group_from_id(grp):
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