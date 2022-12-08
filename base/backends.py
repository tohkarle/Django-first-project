from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q
from .models import User


class EmailBackend(ModelBackend):
    def authenticate(self, request, username_or_email=None, password=None, **kwargs):
        try:
            user = User.objects.get(Q(username__iexact=username_or_email) | Q(email__iexact=username_or_email))
        except User.DoesNotExist:
            User().set_password(password)
            return
        except User.MultipleObjectsReturned:
            user = User.objects.filter(Q(username__iexact=username_or_email) | Q(email__iexact=username_or_email)).order_by('id').first()

        if user.check_password(password) and self.user_can_authenticate(user):
            return user