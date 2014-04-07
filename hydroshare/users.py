from .utils import get_resource_by_shortkey

### User management and authorization API

def set_resource_owner(pk, user):
    """
    Changes ownership of the specified resource to the user specified by a userID.

    REST URL:  PUT /resource/owner/{pid}?user={userID}

    Parameters:
    pid - Unique HydroShare identifier for the resource to be modified
    userID - ID for the user to be set as an owner of the resource identified by pid

    Returns: The pid of the resource that was modified

    Return Type: pid

    Raises:
    Exceptions.NotAuthorized - The user is not authorized
    Exceptions.NotFound - The resource identified by pid does not exist
    Exception.ServiceFailure - The service is unable to process the request
    Note:  This can only be done by the resource owner or a HydroShare administrator.

    """

    res = get_resource_by_shortkey(pk)
    res.owners = [user]
    res.save()
    return pk


DO_NOT_DISTRIBUTE='donotdistribute'
EDIT='edit'
VIEW='view'
PUBLIC='public'
def set_access_rules(pk, user=None, group=None, access=None, allow=False):
    """
    Set the access permissions for an object identified by pid. Triggers a change in the system metadata. Successful
    completion of this operation in indicated by a HTTP response of 200. Unsuccessful completion of this operation must
    be indicated by returning an appropriate exception such as NotAuthorized.

    REST URL:  PUT /resource/accessRules/{pid}/?principaltype=({userID}|{groupID})&principleID={id}&access=(edit|view|donotdistribute)&allow=(true|false)

    Parameters:
    pid - Unique HydroShare identifier for the resource to be modified
    principalType - The type of principal (user or group)
    principalID - Identifier for the user or group to be granted access
    access - Permission to be assigned to the resource for the principal
    allow - True for granting the permission, False to revoke

    Returns: The pid of the resource that was modified

    Return Type: pid

    Raises:
    Exceptions.NotAuthorized - The user is not authorized
    Exceptions.NotFound - The resource identified by pid does not exist
    Exceptions.NotFound - The principal identified by principalID does not exist
    Exception.ServiceFailure - The service is unable to process the request

    Note:  Do not distribute is an attribute of the resource that is set by a user with Full permissions and only
    applies to users with Edit and View privileges. There is no share privilege in HydroShare. Share permission is
    implicit unless prohibited by the Do not distribute attribute. The only permissions in HydroShare are View, Edit and
    Full.

    As-built notes:  TypeError was used as it's a built-in exception Django knows about.  it will result in a
    ServiceFailure if used over the web.

    Also, authorization is not handled in the server-side API.  Server-side API functions run "as root"

    access=public, allow=true will cause the resource to become publicly viewable.

    pid can be a resource instance instead of an identifier (for efficiency)
    """
    access = access.lower()
    if isinstance(pk, basestring):
        res = get_resource_by_shortkey(pk, or_404=False)

    if access == DO_NOT_DISTRIBUTE:
        res.do_not_distribute = allow
        res.save()
    elif access == PUBLIC:
        res.public = allow
        res.save()
    elif access == EDIT:
        if user:
            if allow:
                if not res.edit_users.filter(pk=user.pk).exists():
                    res.edit_users.add(user)
            else:
                if res.edit_users.filter(pk=user.pk).exists():
                    res.edit_users.filter(pk=user.pk).delete()
        elif group:
            if allow:
                if not res.edit_groups.filter(pk=group.pk).exists():
                    res.edit_groups.add(group)
            else:
                if res.edit_groups.filter(pk=group.pk).exists():
                    res.edit_groups.filter(pk=group.pk).delete()
        else:
            raise TypeError('Tried to edit access permissions without specifying a user or group')
    elif access == VIEW:
        if user:
            if allow:
                if not res.view_users.filter(pk=user.pk).exists():
                    res.view_users.add(user)
            else:
                if res.view_users.filter(pk=user.pk).exists():
                    res.view_users.filter(pk=user.pk).delete()
        elif group:
            if allow:
                if not res.view_groups.filter(pk=group.pk).exists():
                    res.view_groups.add(group)
            else:
                if res.view_groups.filter(pk=group.pk).exists():
                    res.view_groups.filter(pk=group.pk).delete()
        else:
            raise TypeError('Tried to view access permissions without specifying a user or group')
    else:
        raise TypeError('access was none of {donotdistribute, public, edit, view}  ')
        


def create_account(*args, **kwargs):
    """
    Create a new user within the HydroShare system.

    REST URL:  POST /accounts

    Parameters: user - An object containing the attributes of the user to be created

    Returns: The userID of the user that was created

    Return Type: userID

    Raises:
    Exceptions.NotAuthorized - The user is not authorized
    Exceptions.InvalidContent - The content of the user object is invalid
    Exception.ServiceFailure - The service is unable to process the request

    Note:  This would be done via a JSON object (user) that is in the POST request. Should set a random password, and
    then send an email to make them verify the account. Unverified accounts can't log-in and are automatically deleted
    after a specified time (according to policy).

    """

    from hs_core.api import UserResource
    ur = UserResource()

    raise NotImplemented()


def update_account(user, *args, **kwargs):
    """
    Update an existing user within the HydroShare system. The user calling this method must have write access to the
    account details.

    REST URL:  PUT /accounts/{userID}

    Parameters: userID - ID of the existing user to be modified

    user - An object containing the modified attributes of the user to be modified

    Returns: The userID of the user that was modified

    Return Type: userID

    Raises:
    Exceptions.NotAuthorized - The user is not authorized
    Exceptions.NotFound - The user identified by userID does not exist
    Exceptions.InvalidContent - The content of the user object is invalid
    Exception.ServiceFailure - The service is unable to process the request

    Note:  This would be done via a JSON object (user) that is in the PUT request.

    """
    raise NotImplemented()


def get_user_info(user):
    """
    Get the information about a user identified by userID. This would be their profile information, groups they belong to, etc.

    REST URL:  GET /accounts/{userID}

    Parameters: userID - ID of the existing user to be modified

    Returns: An object containing the details for the user

    Return Type: user

    Raises:
    Exceptions.NotAuthorized - The user is not authorized
    Exceptions.NotFound - The user identified by userID does not exist
    Exception.ServiceFailure - The service is unable to process the request
    """
    raise NotImplemented()


def list_users(query=None, status=None, start=None, count=None):
    """
    List the users that match search criteria.

    REST URL:  GET /accounts?query={query}[&status={status}&start={start}&count={count}]

    Parameters:
    query - a string specifying the query to perform
    status - (optional) parameter to filter users returned based on status
    start=0 -  (optional) the zero-based index of the first value, relative to the first record of the resultset that matches the parameters
    count=100 - (optional) the maximum number of results that should be returned in the response

    Returns: An object containing a list of userIDs that match the query. If none match, an empty list is returned.

    Return Type: userList

    Raises:
    Exceptions.NotAuthorized - The user is not authorized
    Exception.ServiceFailure - The service is unable to process the request

    """
    raise NotImplemented()


def list_groups(query=None, status=None, start=None, count=None):
    """
    List the groups that match search criteria.

    REST URL:  GET /groups?query={query}[&status={status}&start={start}&count={count}]

    Parameters:
    query - a string specifying the query to perform
    status - (optional) parameter to filter groups returned based on status
    start=0 - (optional) the zero-based index of the first value, relative to the first record of the resultset that matches the parameters
    count=100 - (optional) the maximum number of results that should be returned in the response

    Returns: An object containing a list of groupIDs that match the query. If none match, an empty list is returned.

    Return Type: groupList

    Raises:
    Exceptions.NotAuthorized - The user is not authorized
    Exception.ServiceFailure - The service is unable to process the request

    """
    raise NotImplemented()


def create_group(name):
    """
    Create a group within HydroShare. Groups are lists of users that allow all members of the group to be referenced by listing solely the name of the group. Group names must be unique within HydroShare. Groups can only be modified by users listed as group owners.

    REST URL:  POST /groups

    Parameters: group - An object containing the attributes of the group to be created

    Returns: The groupID of the group that was created
    Return Type: groupID

    Raises:
    Exceptions.NotAuthorized - The user is not authorized
    Exceptions.InvalidContent - The content of the group object is invalid
    Exceptions.GroupNameNotUnique - The name of the group already exists in HydroShare
    Exception.ServiceFailure - The service is unable to process the request

    Note:  This would be done via a JSON object (group) that is in the POST request. May want to add an email verification step to avoid automated creation of fake groups. The creating user would automatically be set as the owner of the created group.
    """

    raise NotImplemented()


def update_group(name, *members):
    """
    Modify details of group identified by groupID or add or remove members to/from the group. Group members can be modified only by an owner of the group, otherwise a NotAuthorized exception is thrown. Group members are provided as a list of users that replace the group membership.

    REST URL:  PUT /groups/{groupID}

    Parameters:
    groupID - groupID of the existing group to be modified
    group - An object containing the modified attributes of the group to be modified and the modified list of userIDs in the group membership

    Returns: The groupID of the group that was modified

    Return Type: groupID

    Raises:
    Exceptions.NotAuthorized - The user is not authorized
    Exceptions.NotFound - The group identified by groupID does not exist
    Exceptions.InvalidContent - The content of the group object is invalid
    Exception.ServiceFailure - The service is unable to process the request

    Note:  This would be done via a JSON object (group) that is in the PUT request.
    """

    raise NotImplemented()


def list_group_members(name):
    """
    Get the information about a group identified by groupID. For a group this would be its description and membership list.

    REST URL:  GET /group/{groupID}

    Parameters: groupID - ID of the existing user to be modified

    Returns: An object containing the details for the group

    Return Type: group

    Raises:
    Exceptions.NotAuthorized - The user is not authorized
    Exceptions.NotFound - The group identified by groupID does not exist
    Exception.ServiceFailure - The service is unable to process the request
    """
    raise NotImplemented()


def set_group_owner(group, user):
    """
    Adds ownership of the group identified by groupID to the user specified by userID. This can only be done by a group owner or HydroShare administrator.

    REST URL:  PUT /groups/{groupID}/owner/?user={userID}

    Parameters: groupID - groupID of the existing group to be modified

    userID - userID of the existing user to be set as the owner of the group

    Returns: The groupID of the group that was modified

    Return Type: groupID

    Raises:
    Exceptions.NotAuthorized - The user is not authorized
    Exceptions.NotFound - The group identified by groupID does not exist
    Exceptions.NotFound - The user identified by userID does not exist
    Exception.ServiceFailure - The service is unable to process the request
 """

def delete_group_owner(group, user):
    """
    Removes a group owner identified by a userID from a group specified by groupID. This can only be done by a group owner or HydroShare administrator.

    REST URL:  DELETE /groups/{groupID}/owner/?user={userID}

    Parameters: groupID - groupID of the existing group to be modified

    userID - userID of the existing user to be removed as the owner of the group

    Returns: The groupID of the group that was modified

    Return Type: groupID

    Raises:
    Exceptions.NotAuthorized - The user is not authorized
    Exceptions.NotFound - The group identified by groupID does not exist
    Exceptions.NotFound - The user identified by userID does not exist
    Exceptions.InvalidRequest - The request would result in removal of the last remaining owner of the group
    Exception.ServiceFailure - The service is unable to process the request

    Note:  A group must have at least one owner.
    """


def get_resource_list(query_type=None, group_id=None, user_id=None, from_date=None, to_date=None, start=None,
                      count=None):
    """
    Return a list of pids for Resources that have been shared with a group identified by groupID.
    REST URL:  GET /resourceList?groups__contains={groupID}

    Parameters:
    queryType - string specifying the type of query being performed
    groupID - groupID of the group whose list of shared resources is to be returned

    Returns: A list of pids for resources that have been shared with the group identified by groupID.  If no resources have been shared with a group, an empty list is returned.

    Return Type: resourceList

    Raises:
    Exceptions.NotAuthorized - The user is not authorized
    Exceptions.NotFound - The group identified by groupID does not exist
    Exception.ServiceFailure - The service is unable to process the request

    Note:  See http://django-tastypie.readthedocs.org/en/latest/resources.html#basic-filtering for implementation details and example. We may want to modify this method to return more than just the pids for resources so that some metadata for the list of resources returned could be displayed without having to call HydroShare.getScienceMetadata() and HydroShare.GetSystemMetadata() for every resource in the returned list.

    """
    raise NotImplemented()

