
from . import utils
from mezzanine.generic.models import Rating, ThreadedComment
from django.core.exceptions import ObjectDoesNotExist
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


def annotate_resource(pk, annotation, user, reply_to=None):
    """
    NOT IN API DOC
    """
    if not isinstance(annotation, basestring):
        raise ValueError("Comment was not found to be a string value")

    if len(annotation) == 0:
        raise ValueError("No comment was provided")

    res = utils.get_resource_by_shortkey(pk)
    user = utils.user_from_id(user)
    if reply_to:
        try:
            comment_to_reply = ThreadedComment.objects.get(pk=reply_to)
            if comment_to_reply.content_object != res:
                raise ValueError("Invalid reply_to comment")

            # check if this comment has already been replied
            if comment_to_reply.replied_to:
                raise ValueError("Invalid reply_to comment")

            # Note: current implementation allows a user to reply to his/her comment
            # If needed we can prevent that

        except ObjectDoesNotExist:
            raise ObjectDoesNotExist(reply_to)

    new_comment = ThreadedComment.objects.create(content_object=res, user=user, comment=annotation)
    if reply_to:
        comment_to_reply.replied_to = new_comment
        comment_to_reply.save()

    return new_comment


def endorse_annotation(name):
    """
    NOT IN API DOC
    """
    raise NotImplemented()

def endorse_resource(pk, user):
    res = utils.get_resource_by_shortkey(pk)
    user = utils.user_from_id(user)
    # first check this user has not already endorsed this resource
    # then create a Rating object using the res and user
    # when creating the Rating object set the value attribute to 1 (+1)
    rating = Rating.objects.filter(object_pk=res.id, user=user).first()
    if not rating:
        rating = Rating.objects.create(content_object=res, user=user, value=1)

    return rating
