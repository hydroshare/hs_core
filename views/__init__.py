from __future__ import absolute_import
from django.contrib.auth.models import Group, User
from django.http import HttpResponseRedirect, HttpResponse
from mezzanine.conf import settings
from django import forms
from hs_core.hydroshare import get_resource_list
from hs_core.hydroshare.utils import get_resource_by_shortkey, resource_modified
from .utils import authorize
from hs_core.models import ResourceFile, GenericResource
import requests
from django.core import exceptions as ex
from mezzanine.pages.page_processors import processor_for

from . import users_api
from . import discovery_api
from . import resource_api
from . import social_api


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
    resource_modified(res, request.user)
    return HttpResponseRedirect(request.META['HTTP_REFERER'])


def add_citation(request, shortkey, *args, **kwargs):
    res, _, _ = authorize(request, shortkey, edit=True, full=True, superuser=True)
    res.dublin_metadata.create(term='REF', content=request.REQUEST['content'])
    resource_modified(res, request.user)
    return HttpResponseRedirect(request.META['HTTP_REFERER'])


def add_metadata_term(request, shortkey, *args, **kwargs):
    res, _, _ = authorize(request, shortkey, edit=True, full=True, superuser=True)
    res.dublin_metadata.create(
        term=request.REQUEST['term'],
        content=request.REQUEST['content'],
        qualifier=request.REQUEST.get('qualifier', None) or None # or None will set none instead of blank.
    )
    resource_modified(res, request.user)
    return HttpResponseRedirect(request.META['HTTP_REFERER'])

def delete_file(request, shortkey, f, *args, **kwargs):
    res, _, _ = authorize(request, shortkey, edit=True, full=True, superuser=True)
    fl = res.files.filter(pk=int(f)).first()
    fl.resource_file.delete()
    fl.delete()
    resource_modified(res, request.user)
    return HttpResponseRedirect(request.META['HTTP_REFERER'])


def delete_resource(request, shortkey, f, *args, **kwargs):
    res, _, _ = authorize(request, shortkey, edit=True, full=True, superuser=True)
    for fl in res.files.all():
        fl.resource_file.delete()
        fl.delete()
    for bag in res.bags.all():
        bag.bag.delete()
        bag.delete()
    res.delete()
    return HttpResponseRedirect('/my-resources/')


def publish(request, shortkey, *args, **kwargs):
    res, _, _ = authorize(request, shortkey, edit=True, full=True, superuser=True)
    res.edit_users = []
    res.edit_groups = []
    res.published_and_frozen = True
    res.doi = "to be assigned"
    res.save()
    resource_modified(res, request.user)
    return HttpResponseRedirect(request.META['HTTP_REFERER'])

def change_permissions(request, shortkey, *args, **kwargs):
    res, _, _ = authorize(request, shortkey, edit=True, full=True, superuser=True)
    t = request.POST['t']
    values = [int(k) for k in request.POST.getlist('designees', [])]
    if t == 'owners':
        res.owners = User.objects.in_bulk(values)
    elif t == 'edit_users':
        res.edit_users = User.objects.in_bulk(values)
    elif t == 'edit_groups':
        print 'changing edit groups to: {0}'.format(values)
        res.edit_groups = Group.objects.in_bulk(values)
    elif t == 'view_users':
        res.view_users = User.objects.in_bulk(values)
    elif t == 'view_groups':
        res.view_groups = Group.objects.in_bulk(values)

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


class FilterForm(forms.Form):
    start = forms.IntegerField(required=False)
    published = forms.BooleanField(required=False)
    edit_permission = forms.BooleanField(required=False)
    creator = forms.ModelChoiceField(queryset=User.objects.all(), required=False)
    user = forms.ModelChoiceField(queryset=User.objects.all(), required=False)
    from_date = forms.DateTimeField(required=False)



@processor_for('my-resources')
def my_resources(request, page):
    frm = FilterForm(data=request.REQUEST)
    if frm.is_valid():
        user = frm.cleaned_data['user'] or request.user
        edit_permission = frm.cleaned_data['edit_permission'] or False
        published = frm.cleaned_data['published'] or False
        start = frm.cleaned_data['start'] or 0
        from_date = frm.cleaned_data['from_date'] or None

        res = set()
        for lst in get_resource_list(
                user=user,
                count=20,
                published=published,
                edit_permission=edit_permission,
                start=start,
                from_date=from_date
        ).values():
            res = res.union(lst)

        res = sorted(list(res), lambda x: x.title)
        return {
            'resources': res,
            'first': start,
            'last': start+len(res),
            'ct': len(res),
            'dcterms' : (\
                ('AB', 'Abstract'),
                ('AR', 'AccessRights'),
                ('AM', 'AccrualMethod'),
                ('AP', 'AccrualPeriodicity'),
                ('APL', 'AccrualPolicy'),
                ('ALT', 'Alternative'),
                ('AUD', 'Audience'),
                ('AVL', 'Available'),
                ('BIB', 'BibliographicCitation'),
                ('COT', 'ConformsTo'),
                ('CN', 'Contributor'),
                ('CVR', 'Coverage'),
                ('CRD', 'Created'),
                ('CR', 'Creator'),
                ('DT', 'Date'),
                ('DTA', 'DateAccepted'),
                ('DTC', 'DateCopyrighted'),
                ('DTS', 'DateSubmitted'),
                ('DSC', 'Description'),
                ('EL', 'EducationLevel'),
                ('EXT', 'Extent'),
                ('FMT', 'Format'),
                ('HFMT', 'HasFormat'),
                ('HPT', 'HasPart'),
                ('HVS', 'HasVersion'),
                ('ID', 'Identifier'),
                ('IM', 'InstructionalMethod'),
                ('IFMT', 'IsFormatOf'),
                ('IPT', 'IsPartOf'),
                ('IREF', 'IsReferencedBy'),
                ('IREP', 'IsReplacedBy'),
                ('IREQ', 'IsRequiredBy'),
                ('IS', 'Issued'),
                ('IVSN', 'IsVersionOf'),
                ('LG', 'Language'),
                ('LI', 'License'),
                ('ME', 'Mediator'),
                ('MED', 'Medium'),
                ('MOD', 'Modified'),
                ('PRV', 'Provenance'),
                ('PBL', 'Publisher'),
                ('REF', 'References'),
                ('REL', 'Relation'),
                ('REP', 'Replaces'),
                ('REQ', 'Requires'),
                ('RT', 'Rights'),
                ('RH', 'RightsHolder'),
                ('SRC', 'Source'),
                ('SP', 'Spatial'),
                ('SUB', 'Subject'),
                ('TOC', 'TableOfContents'),
                ('TE', 'Temporal'),
                ('T', 'Title'),
                ('TYP', 'Type'),
                ('VA', 'Valid'),
    )
        }



@processor_for(GenericResource)
def add_dublin_core(request, page):
    from dublincore import models as dc

    class DCTerm(forms.ModelForm):
        class Meta:
            model=dc.QualifiedDublinCoreElement
            fields = ['term','qualifier','content']

    cm = page.get_content_model()
    try:
        abstract = cm.dublin_metadata.filter(term='AB').first().content
    except:
        abstract = None

    return {
        'dublin_core' : [t for t in cm.dublin_metadata.all().exclude(term='AB').exclude(term='REF')],
        'abstract' : abstract,
        'citations' : [t.content for t in cm.dublin_metadata.filter(term='REF')],
        'resource_type' : cm._meta.verbose_name,
        'dcterm_frm' : DCTerm(),
        'bag' : cm.bags.first(),
        'users' : User.objects.all(),
        'groups' : Group.objects.all(),
        'owners' : set(cm.owners.all()),
        'view_users' : set(cm.view_users.all()),
        'view_groups' : set(cm.view_groups.all()),
        'edit_users' : set(cm.edit_users.all()),
        'edit_groups' : set(cm.edit_groups.all()),

    }



# FIXME need a task somewhere that amounts to checking inactive accounts and deleting them after 30 days.