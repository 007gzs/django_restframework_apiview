# encoding: utf-8
from __future__ import absolute_import, unicode_literals


from example_app.models import User


class UserBackend(object):

    def authenticate(self, example_username=None, example_password=None, **kwargs):
        if example_username is None or example_password is None:
            return None
        user = User.objects.filter(username=example_username).first()
        if user and user.check_password(example_password) and self.user_can_authenticate(user):
            return user

    def user_can_authenticate(self, user):
        """
        Reject users with is_active=False. Custom user models that don't have
        that attribute are allowed.
        """
        is_delete = getattr(user, 'is_delete', None)
        return is_delete is False or is_delete is None

    def get_user(self, user_id):
        try:
            user = User.objects.get(pk=user_id)
        except BBUserAuth.DoesNotExist:
            return None
        return user if self.user_can_authenticate(user) else None

