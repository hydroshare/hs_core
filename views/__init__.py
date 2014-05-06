from __future__ import absolute_import

from django.http import HttpResponseRedirect, HttpResponse
from hs_core.hydroshare.utils import get_resource_by_shortkey
from hs_core.views.utils import authorize
from .users_api import *
from .discovery_api import *
from .resource_api import *
from .social_api import *
from hs_core.models import ResourceFile
from django import forms
from django.conf import settings
import requests
from django.core import exceptions as ex
from mezzanine.pages.page_processors import processor_for

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


class CaptchaVerifyForm(forms.Form):
    challenge = forms.CharField()
    response = forms.CharField()

def verify_captcha(request):
    f = CaptchaVerifyForm(request.POST)
    if f.is_valid():
        params = dict(f.cleaned_data)
        params['privatekey'] = getattr(settings, 'RECAPTCHA_PRIVATE_KEY', '6LegBPMSAAAAADZZagdp5oW7M474j_iXsnBSSfhy')
        params['remoteip'] = request.META['REMOTE_ADDR']
        resp = requests.post('http://www.google.com/recaptcha/api/verify', params=params)
        lines = resp.text.split('\n')
        if lines[0].startswith('false'):
            raise ex.PermissionDenied('captcha failed')
        else:
            return HttpResponse('true', content_type='text/plain')

@processor_for('resend-verification-email')
def resend_verification_email(request, page):
    pass # FIXME not implemented

# FIXME need a task somewhere that amounts to checking inactive accounts and deleting them after 30 days.