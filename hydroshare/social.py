

# social API

def endorse_resource(name):
    """
    NOT IN API DOC
    """
    raise NotImplemented()


def follow_user(name):
    """
    NOT IN API DOC
    """
    raise NotImplemented()


def delete_follow_user(name):
    """
    NOT IN API DOC
    """
    raise NotImplemented()


def follow_resource(name):
    """
    NOT IN API DOC
    """
    raise NotImplemented()


def delete_follow_resource(name):
    """
    NOT IN API DOC
    """
    raise NotImplemented()


def follow_group(name):
    """
    NOT IN API DOC
    """
    raise NotImplemented()


def delete_follow_group(name):
    """
    NOT IN API DOC
    """
    raise NotImplemented()


def annotate_resource(name):
    """
    NOT IN API DOC
    """
    raise NotImplemented()


def endorse_comment(comment, resource, endorse=True, user=None):
    """
    Adds a +1 to the comment from the user.  Checks first to make sure the user has not +1'd previously.

    :param comment: The comment ID (primary key)
    :param endorse: True for a +1.  False to remove any previous endorsement.
    :param resource: The resource (for authorizaton purposes)
    :param user: The user endorsing the comment
    :return: The comment instance (ThreadedComment)
    """

    # first, make sure the user hasn't already added a rating to this comment.

    # if they have and endorse is true, either throw an exception or just return without doing anything.

    # if they have and endorse is false, delete the Rating object

    # if they haven't and endorse is true, create a new rating object and add it to the threadedcomment instance,
    # populating it with a "1".

    # otehrwise throw an exception or just return (document which you do).

    raise NotImplemented()


def comment_on_resource(comment, resource, user=None, in_reply_to=None):
    """
    Add a comment to a resource or in reply to another comment.

    :param comment: The text of the comment to add (HTML is allowed)
    :param user: The user id or username (use user_from_id(user) to resovle the object instance)
    :param in_reply_to: this should be a comment ID or a ThreadedComment instance (resolve this yourself)
    :param resource: This should be a resource instance or shortkey.  get_resource_from_shortkey can be passed either.
    :return: The comment instance (ThreadedComment)
    """

    # ThreadedComment.objects.create(...)

    raise NotImplemented()


