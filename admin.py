from mezzanine.pages.admin import PageAdmin
from django.contrib.gis import admin
from .models import *
from dublincore.models import QualifiedDublinCoreElement

class InlineDublinCoreMetadata(generic.GenericTabularInline):
    model = QualifiedDublinCoreElement

class GenericResourceAdmin(PageAdmin):
    inlines = PageAdmin.inlines + [InlineDublinCoreMetadata]

admin.site.register(GenericResource, GenericResourceAdmin)
