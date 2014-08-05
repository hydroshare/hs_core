import autocomplete_light
from django.contrib.auth.models import User, Group

autocomplete_light.register(User,
    search_fields=['username','email','first_name','last_name'])

autocomplete_light.register(Group,
    search_fields=['name'])