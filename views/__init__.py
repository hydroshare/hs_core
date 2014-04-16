from __future__ import absolute_import

from django.http import HttpResponseRedirect
from hs_core.hydroshare.utils import get_resource_by_shortkey
from hs_core.views.utils import authorize
from .users_api import *
from .discovery_api import *
from .resource_api import *
from .social_api import *
from hs_core.models import ResourceFile

def short_url(request, *args, **kwargs):
    try:
        shortkey = kwargs['shortkey']
    except KeyError:
        raise TypeError('shortkey must be specified...')

    m = get_resource_by_shortkey(shortkey)
    return HttpResponseRedirect(m.get_absolute_url())


def add_file_to_resource(request, *args, **kwargs):
    try:
        shortkey = kwargs['shortkey']
    except KeyError:
        raise TypeError('shortkey must be specified...')

    res, _, _ = authorize(request, shortkey, edit=True, full=True, superuser=True)
    res.files.add(ResourceFile(content_object=res, resource_file=request.FILES['file']))
    return HttpResponseRedirect(request.META['HTTP_REFERER'])

