from __future__ import absolute_import

from django.core.exceptions import PermissionDenied
from hs_core import hydroshare
from ga_resources.utils import get_user
from hs_core.hydroshare.utils import get_resource_by_shortkey

def authorize(request, res_id, edit=False, view=False, full=False, superuser=False, raises_exception=True):
    """
    Authorizes the user making this request for the OR of the parameters.  If the user has ANY permission set to True in
    the parameter list, then this returns True else False.
    """
    user = get_user(request)
    res = hydroshare.utils.get_resource_by_shortkey(res_id)

    has_edit = res.edit_users.filter(pk=user.pk).exists()
    has_view = res.view_users.filter(pk=user.pk).exists()
    has_full = res.owners.filter(pk=user.pk).exists()

    authorized = (edit and has_edit) or (view and has_view) or (full and has_full) or (superuser and user.is_superuser())
    if raises_exception and not authorized:
        raise PermissionDenied()
    else:
        return res, authorized, user
