from rest_framework.serializers import ModelSerializer
from base.models import Room


# Turns python objects into json objects so they can be passed into the Response() from djangorestframework.
# This is essentially like a 'form' but in json objects settings(?), and now we need to pass argument into this class. which is going to be the actual object we want to serialize.
class RoomSerializer(ModelSerializer):
    class Meta:
        # This function copies the fields from model Room in models.py and serialize it (turning it into json object).
        model = Room
        fields = '__all__'

