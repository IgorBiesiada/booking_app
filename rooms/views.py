import datetime
from django.urls import reverse

from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, UpdateView, DeleteView, DetailView
from django.contrib import messages

from . import models
from . models import Room, Reservation


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
            return render(request, 'rooms/add_room.html', context={'error': 'Sala o podanej nazwie już istnieje'})

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

class RoomModifyView(UpdateView):
    model = models.Room
    fields = ('room_name', 'room_capacity', 'projector_available')
    template_name = 'rooms/update_form.html'
    success_url = reverse_lazy('rooms:room-list')

    def get_object(self, queryset=None):
        pk = self.kwargs.get('id')
        return get_object_or_404(Room, id=pk)


    def form_valid(self, form):
        room_name = form.cleaned_data['room_name']
        room_capacity = form.cleaned_data['room_capacity']

        if Room.objects.filter(room_name=room_name).exclude(id=self.object.id).exists():
            form.add_error('room_name', 'Pokój o tej nazwie istnieje')
            return self.form_invalid(form)

        if room_capacity <= 0:
            form.add_error('room_capacity', 'Liczba miejsc musi być większa niz 0')
            return self.form_invalid(form)

        messages.success(self.request, 'Aktualizacja udana')
        return super().form_valid(form)

class ReservationView(View):
    def get(self, request, room_id):
        room = Room.objects.get(id=room_id)
        reservations = room.reservations.filter(date__gte=str(datetime.date.today())).order_by('date')
        return render(request, 'rooms/reservation.html', {'room': room, 'reservations': reservations})

    def post(self, request, room_id):
        room = Room.objects.get(id=room_id)
        date = request.POST.get('reservation-date')
        comment = request.POST.get('comment')

        reservations = room.reservations.filter(date__gte=str(datetime.date.today())).order_by('date')

        if not date:
            return render(request, 'rooms/reservation.html',
                          context={'room': room, 'reservations': reservations, 'error': 'Nie podano daty rezerwacji.'})

        if Reservation.objects.filter(room=room, date=date):
            return render(request, 'rooms/reservation.html', context={'room': room, 'reservations': reservations, 'error': 'Sala jest juz zarezerwowana'})

        reservation_date = datetime.datetime.strptime(date, "%Y-%m-%d").date()

        if reservation_date < datetime.date.today():
            return render(request, 'rooms/reservation.html', context={'room': room, 'reservations': reservations, 'error': 'data jest z przeszłości'})

        Reservation.objects.create(room=room, date=date, comment=comment)
        return redirect('rooms:room-list')

class DetailRoomView(View):
    def get(self, request, room_id):
        room = Room.objects.get(id=room_id)
        reservations = room.reservations.filter(date__gte=str(datetime.date.today())).order_by('date')
        return render(request, 'rooms/detailed_view.html', context={'room': room, 'reservations': reservations})


