from django.db.models import get_model, get_models
from django.http import Http404
from django.shortcuts import get_object_or_404
import os
import shutil
from hs_core.models import AbstractResource, Bags
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User, Group
import arrow
import bagit

cached_resource_types = None

def get_resource_types():
    global cached_resource_types
    cached_resource_types = filter(lambda x: issubclass(x, AbstractResource), get_models()) if\
        not cached_resource_types else cached_resource_types
    return cached_resource_types


def get_resource_instance(app, model_name, pk, or_404=True):
    model = get_model(app, model_name)
    if or_404:
        get_object_or_404(model, pk=pk)
    else:
        model.objects.get(pk=pk)


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
            except TypeError:
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


def create_bag(resource):
    from mezzanine.conf import settings
    import importlib
    import zipfile

    dest_prefix = getattr(settings, 'BAGIT_STORAGE', '/tmp')
    src_prefix = os.path.join(settings.MEDIA_ROOT, resource.short_id)

    bagit_path = os.path.join(dest_prefix, resource.short_id, arrow.get(resource.updated).format("YYYY.MM.DD.HH.mm.ss"))
    data_path = os.path.join(bagit_path, 'data', 'contents')
    visualization_path = os.path.join(bagit_path, 'data', 'visualization')
    contents_path = os.path.join(bagit_path, 'data', 'contents')

    try:
        os.makedirs(bagit_path)
    except:
        pass

    try:
        os.makedirs(data_path)
    except:
        pass

    try:
        os.makedirs(visualization_path)
    except:
        pass

    try:
        os.makedirs(contents_path)
    except:
        pass

    try:
        shutil.copytree(src_prefix, dest_prefix)
    except:
        pass

    with open(bagit_path + '/resourcemetadata.json', 'w') as out:
        tastypie_module = resource._meta.app_label + '.api'        # the module name should follow this convention
        tastypie_name = resource._meta.object_name + 'Resource'    # the classname of the Resource seralizer
        tastypie_api = importlib.import_module(tastypie_module)    # import the module
        serializer = getattr(tastypie_api, tastypie_name)()        # make an instance of the tastypie resource
        bundle = serializer.build_bundle(obj=resource)             # build a serializable bundle out of the resource
        out.write(serializer.serialize(None, serializer.full_dehydrate(bundle), 'application/json'))

    bag = bagit.make_bag(bagit_path, checksum=['md5'], bag_info={
        'title': resource.title,
        'author': resource.owners.all()[0].username,
        'author_email': resource.owners.all()[0].email,
        'version': arrow.get(resource.updated).format("YYYY.MM.DD.HH.mm.ss"),
        'resource_type': '.'.join((resource._meta.app_label, resource._meta.object_name)),
        'hydroshare_version': getattr(settings, 'HYDROSHARE_VERSION', "R1 development"),
        'shortkey': resource.short_id,
        'slug': resource.slug
    })

    def make_zipfile(output_filename, source_dir):
        relroot = os.path.abspath(os.path.join(source_dir, os.pardir))
        with zipfile.ZipFile(output_filename, "w", zipfile.ZIP_DEFLATED) as zip:
            for root, dirs, files in os.walk(source_dir):
                # add directory (needed for empty dirs)
                zip.write(root, os.path.relpath(root, relroot))
                for file in files:
                    filename = os.path.join(root, file)
                    if os.path.isfile(filename): # regular files only
                        arcname = os.path.join(os.path.relpath(root, relroot), file)
                        zip.write(filename, arcname)

    zf = os.path.join(dest_prefix, resource.short_id) + ".zip"

    make_zipfile(output_filename=zf, source_dir=bagit_path)
    Bags.objects.create(
        content_object=resource,
        path=zf,
        timestamp=resource.updated
    )

    return bag