from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
# from django.contrib.auth.forms import UserCreationForm
from .models import Room, Topic, Message, User
from .forms import RoomForm, UserForm, SignUpForm


# Create your views here.


def loginPage(request):
    page = 'login'
    # If user is loged in, and tries to go to the login page, redirect the user to home page.
    if request.user.is_authenticated:
        return redirect('home')

    # This means 'if users enter their information and send the information to the backend'.
    if request.method == 'POST':
        username_or_email = request.POST.get('username_or_email').lower()
        password = request.POST.get('password')

        # try:
        #     user = User.objects.get(username = username)
        # except:
        #     messages.error(request, 'User does not exist.')
        
        # authenticate() returns the QueryDict data if the username and password matches that of what the users enter, else it returns None.
        user = authenticate(request, username_or_email = username_or_email, password = password)

        if user is not None:
            # login() adds the session of the user in the database, and allows the user to be loged in.
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Username or password does not exist.')

    context = {'page' : page}
    return render(request, 'base/login_register.html', context)


def logoutUser(request):
    logout(request)
    return redirect('home')


def registerPage(request):
    page = 'register'
    form = SignUpForm()

    if request.method == 'POST':
        # In this case, request.POST returns all the sign-up information from the user in QueryDict.
        form = SignUpForm(request.POST)
        if form.is_valid():
            # Basically accessing the data for customization before saving it to the database - If you call save() with commit=False, then it will return an object that hasn’t yet been saved to the database. In this case, it’s up to you to call save() on the resulting model instance. This is useful if you want to do custom processing on the object before saving it, or if you want to use one of the specialized model saving options.
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'An error has occurred during registration.')

    context = {
        'page' : page,
        'form' : form,
    }
    return render(request, 'base/login_register.html', context)


def home(request):
    # request.POST is when the server(?) send in the data that we can play around with(?).
    # request.GET is when the server(?) asks for the data it needs.
    # request.GET returns the QueryDict of data requested by server(?).
    # request.GET.get('q') returns the value of the key 'q', in this case would be the topic.name.
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    # It will filter the Room strictly according to the topic name.
    # rooms = Room.objects.filter(topic__name=q)
    # It will filter the Room according to if topic name contains q, non-case sensitive. E.g. if topic__name == 'Python3' and q == 'Python', the Room under Python3 will also show.
    rooms = Room.objects.filter(
        # Q is an inbuilt function from django.db.models that allows us to include these criterias in an 'OR' or 'AND situation, so that in this case the function can filter according to the first OR second OR third criteria.
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q)
    )
    topics = Topic.objects.all()[0:5]
    # Again, .count() is an inbuilt Django method that returns the length of the QuerySet. Basically a QuerySet is the data that is retrieved after being processed, e.g. .all(), .filter(), etc.
    room_count = rooms.count()
    room_messages = Message.objects.filter(
        Q(room__topic__name__icontains=q)    # Filter by the topic of the room, not the room name.
    )

    context = {
        'rooms' : rooms,
        'topics' : topics,
        'room_count' : room_count,
        'room_messages' : room_messages,
    }
    return render(request, 'base/home.html', context)


def room(request, pk):
    room = Room.objects.get(id=pk)
    # .message(name of the model, no captial letter, in models.py that you want to get the data from)_set.all() returns all the data in the model, in this case Message.
    # In this case, Message contains some attributes/properties/data from Room, because it has Many-To-One relationship with Room.
    # You need to use room.message_set because you are getting the message in this particular room id.
    # .all() simply means you get all the data from Message without filtering/processing.
    room_messages = room.message_set.all()    # .order_by('-created') simply means the message will now be ordered by the time of creation and the '-' at the front indicates descending order, meaning the latest one will be at the top. It was removed afterwards because we can do it directly in the models.py using class Meta.
    participants = room.participants.all()

    if request.method == 'POST':
        # .create() creates the link between the attributes in the Message model to that from request.POST.
        room_message = Message.objects.create(
            user = request.user,
            room = room,
            body = request.POST.get('body'),    # 'body' is the name="body" of the input of the comment.
        )
        # .add() adds request.user into the participants field/data in the Room model. 
        room.participants.add(request.user)
        return redirect('room', pk=room.id)

    context = {
        'room' : room,
        'room_messages' : room_messages,
        'participants' : participants,
    }
    return render(request, 'base/room.html', context)


@login_required(login_url='login')
def deleteMessage(request, pk):
    room_message = Message.objects.get(id=pk)
    room = room_message.room

    if request.user != room_message.user:
        return HttpResponse('You are not allowed here!')

    if request.method == 'POST':
        # Inbuilt method that deletes the data from the database.
        room_message.delete()
        print(request.POST)
        # Redirect back to the previous page where I deleted the message from: home or room.
        next = request.POST.get('next', '/')
        return HttpResponseRedirect(next)
    return render(request, 'base/delete.html', {'obj' : room_message})


def userProfile(request, pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    room_messages = user.message_set.all()
    topics = Topic.objects.all()
    context = {
        'user' : user,
        'rooms' : rooms,
        'room_messages' : room_messages,
        'topics' : topics,
    }
    return render(request, 'base/profile.html', context)



@login_required(login_url='login')
def createRoom(request):
    form = RoomForm()
    topics = Topic.objects.all()
    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        # If the name of the topic is not found in Topic model data, it is going to create the data. This method itself returns two values: first - the data with that topic name; second - the value of True/False for whether the data is not found in the database and is just created.
        topic, created = Topic.objects.get_or_create(name=topic_name)
        Room.objects.create(
            host = request.user,
            topic = topic,
            name = request.POST.get('name'),    # 'name' is the name of the input field for name in room_form.html.
            description = request.POST.get('description'),    # 'description' is the name of the input field for description in room_form.html.
        )
        return redirect('home')
        
        # print(request.POST)
        # request.POST returns the QueryDict (basically just a dictionary) of the data created.
        # RoomForm(requst.POST) fills the form with all those data that is in the QueryDict.
        # And then form.is_valid checks whether the data is valid, not sure what valid means though.
        # form = RoomForm(request.POST)
        # if form.is_valid:
            # .save() method creates and saves a database object from the data bound to the form.
            # Changed to .save(commit=False) because 'host' and 'participants' are now excluded from the RoomForm and so there is no values for these two keys.
            # So we need to access the QueryDict/data using .save(commit=False) and assign the 'host' key to the user that created this form.
            # room = form.save(commit=False)
            # room.host = request.user
            # room.save()
            # The 'home' is the name of the url to the home.html
        

    context = {
        'form' : form,
        'topics' : topics,
    }
    return render(request, 'base/room_form.html', context)


@login_required(login_url='login')
def updateRoom(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)
    topics = Topic.objects.all()

    if request.user != room.host:
        return HttpResponse('You are not allowed here!')

    # When the user updates the details of the Room, similar things happen as when user creates a Room.
    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        room.topic = topic
        room.name = request.POST.get('name')
        room.description = request.POST.get('description')
        room.save()
        return redirect('room', pk=room.id)

        # But one thing that is different is that it needs to save back to the same Room. Therefore the argument instance=room.
        # form = RoomForm(request.POST, instance=room)
        # Check whether the data is valid, and save into database.
        # if form.is_valid:
        #     form.save()
        #     return redirect('home')

    context = {
        'room' : room,
        'form' : form,
        'topics' : topics,
    }
    return render(request, 'base/room_form.html', context)


@login_required(login_url='login')
def deleteRoom(request, pk):
    # We do not need to include room.name because the class Room itself returns the name because of the function __str__ that returns self.name.
    room = Room.objects.get(id=pk)

    if request.user != room.host:
        return HttpResponse('You are not allowed here!')

    if request.method == 'POST':
        # Inbuilt method that deletes the data from the database.
        room.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj' : room})


@login_required(login_url='login')
def updateUser(request):
    form = UserForm(instance=request.user)

    if request.method == 'POST':
        # request.FILES returns whatever files the users submit.
        form = UserForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('user-profile', pk=request.user.id)

    context = {
        'form' : form,
    }
    return render(request, 'base/update_user.html', context)


def topicPage(request):
    # IF no argument, .filter() works like .all()
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    topics = Topic.objects.filter(
        name__icontains = q
    )
    context = {
        'topics' : topics,
    }
    return render(request, 'base/topics.html', context)


def activityPage(request):
    room_messages = Message.objects.all()
    context = {
        'room_messages' : room_messages,
    }
    return render(request, 'base/activity.html', context)