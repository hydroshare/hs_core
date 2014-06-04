from django.contrib.contenttypes import generic
from django.contrib.auth.models import User, Group
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.timezone import now
from mezzanine.pages.models import Page, RichText
from mezzanine.pages.page_processors import processor_for
from uuid import uuid4
from mezzanine.core.models import Ownable
from mezzanine.generic.fields import CommentsField
from mezzanine.conf import settings as s
import os.path
# from dublincore.models import QualifiedDublinCoreElement

class GroupOwnership(models.Model):
    group = models.ForeignKey(Group)
    owner = models.ForeignKey(User)


def get_user(request):
    """authorize user based on API key if it was passed, otherwise just use the request's user.

    :param request:
    :return: django.contrib.auth.User
    """

    from tastypie.models import ApiKey

    if 'api_key' in request.REQUEST:
        api_key = ApiKey.objects.get(key=request.REQUEST['api_key'])
        return api_key.user
    elif request.user.is_authenticated():
        return User.objects.get(pk=request.user.pk)
    else:
        return request.user

class ResourcePermissionsMixin(Ownable):
    creator = models.ForeignKey(User,
        related_name='creator_of_%(app_label)s_%(class)s',
        help_text='This is the person who first uploaded the resource',
    )

    public = models.BooleanField(
        help_text='If this is true, the resource is viewable and downloadable by anyone',
        default=True
    )
    # DO WE STILL NEED owners?
    owners = models.ManyToManyField(User,
        related_name='owns_%(app_label)s_%(class)s',
        help_text='The person who uploaded the resource'
    )
    frozen = models.BooleanField(
        help_text='If this is true, the resource should not be modified',
        default=False
    )
    do_not_distribute = models.BooleanField(
        help_text='If this is true, the resource owner has to designate viewers',
        default=False
    )
    discoverable = models.BooleanField(
        help_text='If this is true, it will turn up in searches.',
        default=True
    )
    published_and_frozen = models.BooleanField(
        help_text="Once this is true, no changes can be made to the resource",
        default=False
    )

    view_users = models.ManyToManyField(User,
         related_name='user_viewable_%(app_label)s_%(class)s',
         help_text='This is the set of Hydroshare Users who can view the resource',
         null=True, blank=True)

    view_groups = models.ManyToManyField(Group,
         related_name='group_viewable_%(app_label)s_%(class)s',
         help_text='This is the set of Hydroshare Groups who can view the resource',
         null=True, blank=True)

    edit_users = models.ManyToManyField(User,
         related_name='user_editable_%(app_label)s_%(class)s',
         help_text='This is the set of Hydroshare Users who can edit the resource',
         null=True, blank=True)

    edit_groups = models.ManyToManyField(Group,
         related_name='group_editable_%(app_label)s_%(class)s',
         help_text='This is the set of Hydroshare Groups who can edit the resource',
         null=True, blank=True)

    class Meta:
        abstract = True

    @property
    def permissions_store(self):
        return s.PERMISSIONS_DB

    def can_add(self, request):
        return self.can_change(request)

    def can_delete(self, request):
        return self.can_change(request)

    def can_change(self, request):
        user = get_user(request)

        if user.is_authenticated():
            if not self.user:
                ret = user.is_superuser
            elif user.pk == self.creator.pk:
                ret = True
            elif user.pk in { o.pk for o in self.owners.all() }:
                ret = True
            elif self.edit_users.filter(pk=user.pk).exists():
                ret = True
            elif self.edit_groups.filter(pk__in=set(g.pk for g in user.groups.all())):
                ret = True
            else:
                ret = False
        else:
            ret = False

        return ret


    def can_view(self, request):
        user = get_user(request)

        if self.public:
            return True
        if user.is_authenticated():
            if not self.user:
                ret = user.is_superuser
            elif user.pk == self.creator.pk:
                ret = True
            elif user.pk in { o.pk for o in self.owners.all() }:
                ret = True
            elif self.view_users.filter(pk=user.pk).exists():
                ret = True
            elif self.view_groups.filter(pk__in=set(g.pk for g in user.groups.all())):
                ret = True
            else:
                ret = False
        else:
            ret = False

        return ret




# this should be used as the page processor for anything with pagepermissionsmixin
# page_processor_for(MyPage)(ga_resources.views.page_permissions_page_processor)
def page_permissions_page_processor(request, page):
    page = page.get_content_model()
    user = get_user(request)

    return {
        "edit_groups": set(page.edit_groups.all()),
        "view_groups": set(page.view_groups.all()),
        "edit_users": set(page.edit_users.all()),
        "view_users": set(page.view_users.all()),
        "can_edit": (user in set(page.edit_users.all()))\
            or (len(set(page.edit_groups.all()).intersection(set(user.groups.all()))) > 0)
    }

class AbstractResource(ResourcePermissionsMixin):
    """
    All hydroshare objects inherit from this mixin.  It defines things that must
    be present to be considered a hydroshare resource.  Additionally, all 
    hydroshare resources should inherit from Page.  This gives them what they
    need to be represented in the Mezzanine CMS.  

    In some cases, it is possible that the order of inheritence matters.  Best
    practice dictates that you list pages.Page first and then other classes:

        class MyResourceContentType(pages.Page, hs_core.AbstractResource):
            ...
    """
    last_changed_by = models.ForeignKey(User, 
        help_text='The person who last changed the resource',
	    related_name='last_changed_%(app_label)s_%(class)s',
	    null=True
    )
    dublin_metadata = generic.GenericRelation(
        'dublincore.QualifiedDublinCoreElement',
        help_text='The dublin core metadata of the resource'
    )
    files = generic.GenericRelation('hs_core.ResourceFile', help_text='The files associated with this resource')
    bags = generic.GenericRelation('hs_core.Bags', help_text='The bagits created from versions of this resource')
    short_id = models.CharField(max_length=32, default=lambda: uuid4().hex, db_index=True)
    doi = models.CharField(max_length=1024, blank=True, null=True, db_index=True,
                           help_text='Permanent identifier. Never changes once it\'s been set.')
    comments = CommentsField()

    def extra_capabilites(self):
        """This is not terribly well defined yet, but should return at the least a JSON serializable object of URL
        endpoints where extra self-describing services exist and can be queried by the user in the form of
        { "name" : "endpoint" }
        """
        return None

    class Meta: 
        abstract = True

def get_path(instance, filename):
    return os.path.join(instance.content_object.short_id, filename)

class ResourceFile(models.Model):
    object_id = models.PositiveIntegerField()
    content_type = models.ForeignKey(ContentType)

    content_object = generic.GenericForeignKey('content_type', 'object_id')
    resource_file = models.FileField(upload_to=get_path, storage=getattr(s, 'RESOURCE_FILE_STORAGE', None))

class Bags(models.Model):
    object_id = models.PositiveIntegerField()
    content_type = models.ForeignKey(ContentType)

    content_object = generic.GenericForeignKey('content_type', 'object_id')
    bag = models.FileField(upload_to='bags', storage=getattr(s, 'BAGIT_STORAGE', None), null=True) # actually never null
    timestamp = models.DateTimeField(default=now, db_index=True)

    class Meta:
        ordering = ['-timestamp']


class GenericResource(Page, RichText, AbstractResource):
    class Meta:
        verbose_name = 'Generic Hydroshare Resource'

    def can_add(self, request):
        return AbstractResource.can_add(self, request)

    def can_change(self, request):
        return AbstractResource.can_change(self, request)

    def can_delete(self, request):
        return AbstractResource.can_delete(self, request)

    def can_view(self, request):
        return AbstractResource.can_view(self, request)

def resource_processor(request, page):
    extra = page_permissions_page_processor(request, page)
    extra['res'] = page.get_content_model()
    extra['dc'] = { m.term_name : m.content for m in extra['res'].dublin_metadata.all() }
    return extra

processor_for(GenericResource)(resource_processor)

@processor_for('resources')
def resource_listing_processor(request, page):
    owned_resources = list(GenericResource.objects.filter(owners__pk=request.user.pk))
    editable_resources = list(GenericResource.objects.filter(owners__pk=request.user.pk))
    viewable_resources = list(GenericResource.objects.filter(public=True))

    return locals()
