from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.


class User(AbstractUser):
    name = models.CharField(max_length=255, null=True)
    email = models.EmailField(unique=True, null=True)
    bio = models.TextField(null=True)
    avatar = models.ImageField(null=True, default="avatar.svg")
    # USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.username


class Topic(models.Model):
    # One-To-Many relationship with Rooom, because a Topic can have multiples Room(s) but a Room can only have one Topic.
    # Of course this is based on how we want it to work, we can also have Many-To-Many relationship with Room, if we want,
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Room(models.Model):
    host = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    # Many-To-One relationship with the Topic, meaning one Room can only have one Topic.
    # Because Topic is defined above Room, so the argument can be Topic, but if Topic is somewhere below Room, then we will havwe to use 'Topic'.
    # Not too sure why need to include null=True, but apparently you need to allow null to be True so that the database is allowed to store no value(?), else there will be an error.
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    # There is already a User model connected to host above, so the related_name= is needed in this case.
    participants = models.ManyToManyField(User, related_name='participants', blank=True)
    updated = models.DateTimeField(auto_now=True)   # Date and time is updated everytime it is saved.
    created = models.DateTimeField(auto_now_add=True)   # Date and time is only added once when it is created.

    # Meta class is an inner class in Django models. Which contain Meta options(metadata) that are used to change the behavior of your model fields like changing order options, whether the model is abstract or not, singular and plural versions of the name etc
    class Meta:
        # This will order the model Room based in ascending order, meaning the most recently created Room will be at the bottom.
        # ordering = ['updated', 'created']
        # This will order Room(s) in descending order of creation, meaning the most recently created Room will be at the top.
        # I think '-updated' is for admin updating/editing of the Room, '-created' is for creation of the room(?). Not sure.
        ordering = ['-updated', '-created']

    # When you reference Room anywhere else, the class Room itself returns the name by default.
    def __str__(self):
        return self.name


class Message(models.Model):
    # User is a preset model by Django.
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # .CASCADE means if Room is deleted, Message will be deleted as well.
    # .SET_NULL means if Room is deleted, Message will still be stored somewhere and not deleted.
    # Many-To-One relationship (symmmetric) with Room, meaning one Room can have many Message(s) but a Message can only be in one Room.
    # models.ForeignKey() is used to define a Many-To-One relationship.
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    body = models.TextField()
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        # This will order the model Room based in ascending order, meaning the most recently created Room will be at the bottom.
        # ordering = ['updated', 'created']
        # This will order Room(s) in descending order of creation, meaning the most recently created Room will be at the top.
        # I think '-updated' is for admin updating/editing of the Room, '-created' is for creation of the room(?). Not sure.
        ordering = ['-updated', '-created']

    def __str__(self):
        # return self.body[0:50]  # Only want the first 50 characters in the preview.
        return self.body


