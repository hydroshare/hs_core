from django.contrib.contenttypes import generic
from django.contrib.auth.models import User, Group
from django.db import models
from mezzanine.pages.models import Page, RichText
from ga_resources.models import PagePermissionsMixin
from mezzanine.core.models import Ownable
from mezzanine.generic.fields import CommentsField
from mezzanine.conf import settings as s
# from dublincore.models import QualifiedDublinCoreElement

def get_user(request):
    from tastypie.models import ApiKey
    """authorize user based on API key if it was passed, otherwise just use the request's user.

    :param request:
    :return: django.contrib.auth.User
    """
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
        default=True
    )
    discoverable = models.BooleanField(
        help_text='If this is true, it will turn up in searches.',
        default=True
    )
    published_and_frozen = models.BooleanField(
        help_text="Once this is true, no changes can be made to the resource",
        default=False
    )

    def storage_key(self, kfor):
        return "{label}.{model}.{key}.{kfor}".format(
            label=self._meta.app_label,
            model=self._meta.module_name,
            key=self.pk,
            kfor=kfor
        )

    class Meta:
        abstract = True

    @property
    def permissions_store(self):
        return s.PERMISSIONS_DB

    @property
    def edit_users(self):
        return set(self.permissions_store.smembers(self.storage_key('edit-users')))

    @property
    def edit_groups(self):
        return set(self.permissions_store.smembers(self.storage_key('edit-groups')))

    @property
    def view_users(self):
        return set(self.permissions_store.smembers(self.storage_key('view-users')))

    @property
    def view_groups(self):
        return set(self.permissions_store.smembers(self.storage_key('view-groups')))


    def add_edit_user(self, user):
        self.permissions_store.sadd(self.storage_key('edit-users'), user if isinstance(user, int) else user.pk)


    def add_view_user(self, user):
        self.permissions_store.sadd(self.storage_key('view-users'), user if isinstance(user, int) else user.pk)


    def add_edit_group(self, group):
        self.permissions_store.sadd(self.storage_key('edit-groups'), group if isinstance(group, int) else group.pk)


    def add_view_group(self, group):
        self.permissions_store.sadd(self.storage_key('view-groups'), group if isinstance(group, int) else group.pk)


    def remove_edit_user(self, user):
        self.permissions_store.srem(self.storage_key('edit-users'), user if isinstance(user, int) else user.pk)


    def remove_view_user(self, user):
        self.permissions_store.srem(self.storage_key('view-users'), user if isinstance(user, int) else user.pk)


    def remove_edit_group(self, group):
        self.permissions_store.srem(self.storage_key('edit-groups'), group if isinstance(group, int) else group.pk)


    def remove_view_group(self, group):
        self.permissions_store.srem(self.storage_key('view-groups'), group if isinstance(group, int) else group.pk)

    def can_add(self, request):
        return self.can_change(request)

    def can_delete(self, request):
        return self.can_change(request)


    def can_change(self, request):
        user = get_user(request)

        ret = True

        if user.is_authenticated():
            if not self.user:
                ret = user.is_superuser
            elif user.pk == self.creator.pk:
                ret = True
            elif user.pk in { o.pk for o in self.owners.all() }:
                ret = True
            else:
                users = self.edit_users
                groups = self.edit_groups

                if len(users) > 0 and user.pk in users:
                    ret = True
                elif len(groups) > 0:
                    ret = user.groups.filter(pk__in=groups).exists()
                else:
                    ret =  False
        else:
            ret = False

        return ret


    def can_view(self, request):
        user = get_user(request)
        ret = True

        if self.public:
            ret = True
        elif user.is_authenticated():
            if self.creator.pk == user.pk:
                ret = True
            elif user.is_superuser:
                ret = True
            elif user.pk in { o.pk for o in self.owners.all() }:
                ret = True
            else:
                users = self.view_users
                groups = self.view_groups

                if len(users) > 0 and user.pk in users:
                    ret = True
                elif len(groups) > 0:
                    ret = user.groups.filter(pk__in=groups).exists()
                else:
                    ret = False
        else:
            ret = False
        return ret

    def copy_permissions_to_children(self, clear_existing=True, recurse=False):
        # pedantically implemented.  should use set logic to minimize changes, but ptobably not important
        for child in self.children:
            if isinstance(child, PagePermissionsMixin):
                if clear_existing:
                    for u in child.edit_users:
                        child.remove_edit_user(u)
                    for u in child.view_users:
                        child.remove_view_user(u)
                    for g in child.edit_groups:
                        child.remove_edit_group(g)
                    for g in child.view_groups:
                        child.remove_view_group(g)

                for u in self.edit_users:
                    child.add_edit_user(u)
                for u in self.view_users:
                    child.add_view_user(u)
                for g in self.edit_groups:
                    child.add_edit_group(g)
                for g in self.view_groups:
                    child.add_view_group(g)

                child.public = self.public
                child.save()
                    
                if recurse:
                    child.copy_permissions_to_children(clear_existing=clear_existing, recurse=recurse)


    def copy_permissions_from_parent(self, clear_existing=True):
        parent = self.parent.get_content_model()
        if isinstance(parent, PagePermissionsMixin):
            if clear_existing:
                for u in self.edit_users:
                    self.remove_edit_user(u)
                for u in self.view_users:
                    self.remove_view_user(u)
                for g in self.edit_groups:
                    self.remove_edit_group(g)
                for g in self.view_groups:
                    self.remove_view_group(g)

            for u in self.parent.edit_users:
                self.add_edit_user(u)
            for u in self.parent.view_users:
                self.add_view_user(u)
            for g in self.parent.edit_groups:
                self.add_edit_group(g)
            for g in self.parent.view_groups:
                self.add_view_group(g)

            self.public = self.parent.public
            self.save()


# this should be used as the page processor for anything with pagepermissionsmixin
# page_processor_for(MyPage)(ga_resources.views.page_permissions_page_processor)
def page_permissions_page_processor(request, page):
    page = page.get_content_model()
    edit_groups = Group.objects.filter(pk__in=page.edit_groups)
    view_groups = Group.objects.filter(pk__in=page.view_groups)
    edit_users = User.objects.filter(pk__in=page.edit_users)
    view_users = User.objects.filter(pk__in=page.view_users)

    return {
        "edit_groups": edit_groups,
        "view_groups": view_groups,
        "edit_users": edit_users,
        "view_users": view_users,
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
	null=True)
    dublin_metadata = generic.GenericRelation(
        'dublincore.QualifiedDublinCoreElement',
        help_text='The dublin core metadata of the resource'
    )
    comments = CommentsField()

    class Meta: 
        abstract = True
 
class GenericResource(Page, RichText, AbstractResource):
    resource_file = models.FileField(
        help_text='This should be a Bagit file containing the resource itself',
        upload_to='generic_resources',
        blank=True, 
        null=True
    )
    resource_url = models.URLField(
        blank=True, 
        null=True
    )

    class Meta:
        verbose_name = 'Generic Hydroshare Resource'

        
