from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import ListView

from . import models
from .models import Room


class AddRoomView(View):

    def get(self, request):
        return render(request, 'rooms/add_room.html')

    def post(self, request):
        name = request.POST.get('room-name')
        capacity = request.POST.get('room-capacity')
        capacity = int(capacity) if capacity else 0
        projector = request.POST.get('room-projector') == "on"

        if not name:
            return render(request, 'rooms/add_room.html', context={'error': 'Nie podano nazwy sali'})
        if capacity <= 0:
            return render(request, 'rooms/add_room.html', context={'error': 'Pojemność sali nie moze byc ujemna'})
        if Room.objects.filter(room_name=name).first():
            return render(request, 'rooms/add_room.html', context={'error': 'Sala o podanej nazwie nie istnieje'})

        Room.objects.create(room_name=name, room_capacity=capacity, projector_available=projector)
        return redirect('rooms:room-list')


class RoomListView(ListView):
    model = models.Room
    template_name = 'rooms/rooms.html'
    context_object_name = 'rooms'

class DeleteRoomView(View):
    def post(self, request, room_id):
        room = Room.objects.get(id=room_id)
        room.delete()
        return redirect('rooms:room-list')
