from __future__ import absolute_import

from django.db.models import get_models
from django.http import HttpResponseRedirect, Http404
from .models import AbstractResource

def short_url(request, *args, **kwargs):
    try:
        shortkey = kwargs['shortkey']
    except KeyError:
        raise Http404()

    models = filter(lambda x: issubclass(x, AbstractResource), get_models())
    for model in models:
        m = model.objects.filter(short_id=shortkey)
        if m.exists():
            return HttpResponseRedirect(m[0].get_absolute_url())
    raise Http404(shortkey)