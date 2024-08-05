from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from .models import Room, Message
import re
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect
from django.contrib import messages

def is_valid_category_name(name):
    return bool(re.match(r'^[a-zA-Z0-9\s]+$', name))

def HomePage(request):
    if request.method == 'POST':
        username = request.POST['username']
        room = request.POST['room']

        if not is_valid_category_name(room):
            messages.error(request ,"Nazwa pokoju nie może zawierać znakow specjalnych")
            return render(request, 'Rooms/index6.html', {'on_edit_record_page': True})

        try:
            get_room = Room.objects.get(room_name=room)
            return redirect('room', room_name=room, username=username)

        except Room.DoesNotExist:
            new_room = Room(room_name=room)
            new_room.save()
            return redirect('room', room_name=room, username=username)

    rooms = Room.objects.all()
    room_count = rooms.count()
    room_names = [room.room_name for room in rooms]

    context = {
        'room_count': room_count,
        'room_names': room_names,
        'on_edit_record_page': True
    }

    return render(request, 'Rooms/index6.html', context)


def MessageView(request, room_name, username):
    get_room = Room.objects.get(room_name=room_name)

    if request.method == 'POST':
        message = request.POST['message']

        print(message)

        new_message = Message(room=get_room, sender=username, message=message)
        new_message.save()

    get_messages = Message.objects.filter(room=get_room)

    context = {
        "messages": get_messages,
        "user": username,
        'on_edit_record_page': True
    }
    return render(request, 'Rooms/message.html', context)

def delete_room(request, room_name):
    room = get_object_or_404(Room, room_name=room_name)
    if request.method == "POST":
        room.delete()
        return redirect('home4')
    return render(request, 'Rooms/Room_delete.html' , {"room": room , 'on_new_record_page': True})

def edit_room(request, room_name):
    room = get_object_or_404(Room, room_name=room_name)

    if request.method == 'POST':
        new_room_name = request.POST['new_room_name']

        if not is_valid_category_name(new_room_name):
            messages.error(request, "Nowa nazwa pokoju nie może zawierać znaków specjalnych")
            return render(request, 'Rooms/room_edit.html', {'room': room, 'on_new_record_page': True})

        if Room.objects.filter(room_name=new_room_name).exclude(pk=room.pk).exists():
            messages.error(request, "Pokój o podanej nazwie już istnieje")
            return render(request, 'Rooms/room_edit.html', {'room': room, 'on_new_record_page': True})

        room.room_name = new_room_name
        room.save()
        messages.success(request, "Nazwa pokoju została zmieniona pomyślnie")
        return redirect('home4')

    return render(request, 'Rooms/room_edit.html', {'room': room, 'on_new_record_page': True})