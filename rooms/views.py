import datetime


from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, UpdateView, DeleteView, DetailView
from django.contrib import messages

from . import models
from . models import Room, Reservation


# View for adding a new room
class AddRoomView(View):

    # Handle GET requests to display the form for adding a room
    def get(self, request):
        return render(request, 'rooms/add_room.html')

    # Handle POST requests to process the form submission
    def post(self, request):
        # Retrieve form data
        name = request.POST.get('room-name')  # Room name
        capacity = request.POST.get('room-capacity')  # Room capacity
        capacity = int(capacity) if capacity else 0  # Convert capacity to int or set to 0 if empty
        projector = request.POST.get('room-projector') == "on"  # Check if projector is available

        # Validate room name
        if not name:
            return render(request, 'rooms/add_room.html', context={'error': 'Room name is required'})
        # Validate room capacity
        if capacity <= 0:
            return render(request, 'rooms/add_room.html', context={'error': 'Room capacity must be greater than zero'})
        # Check if room with the same name already exists
        if Room.objects.filter(room_name=name).first():
            return render(request, 'rooms/add_room.html', context={'error': 'A room with that name already exists'})

        # Create a new room record in the database
        Room.objects.create(room_name=name, room_capacity=capacity, projector_available=projector)
        return redirect('rooms:room-list')  # Redirect to the list of rooms


# View for listing all rooms
class RoomListView(ListView):
    model = models.Room  # Specify the model to use
    template_name = 'rooms/rooms.html'  # Template for rendering the room list
    context_object_name = 'rooms'  # Context variable to use in the template


# View for deleting a room
class DeleteRoomView(View):
    def post(self, request, room_id):
        room = Room.objects.get(id=room_id)  # Retrieve the room by ID
        room.delete()  # Delete the room
        return redirect('rooms:room-list')  # Redirect to the list of rooms


# View for modifying an existing room
class RoomModifyView(UpdateView):
    model = models.Room  # Specify the model to use
    fields = ('room_name', 'room_capacity', 'projector_available')  # Fields to update
    template_name = 'rooms/update_form.html'  # Template for the update form
    success_url = reverse_lazy('rooms:room-list')  # URL to redirect after a successful update

    # Get the room object for the update
    def get_object(self, queryset=None):
        pk = self.kwargs.get('id')  # Get the room ID from URL parameters
        return get_object_or_404(Room, id=pk)  # Return the room object or 404 if not found

    # Validate the form data
    def form_valid(self, form):
        room_name = form.cleaned_data['room_name']  # Get the room name from cleaned data
        room_capacity = form.cleaned_data['room_capacity']  # Get the room capacity

        # Check if another room with the same name exists, excluding the current room
        if Room.objects.filter(room_name=room_name).exclude(id=self.object.id).exists():
            form.add_error('room_name', 'A room with that name already exists')  # Add error to the form
            return self.form_invalid(form)  # Return invalid form

        # Validate room capacity
        if room_capacity <= 0:
            form.add_error('room_capacity', 'Capacity must be greater than zero')  # Add error to the form
            return self.form_invalid(form)  # Return invalid form

        messages.success(self.request, 'Update successful')  # Display success message
        return super().form_valid(form)  # Proceed with form submission


# View for handling room reservations
class ReservationView(View):
    # Handle GET requests to display room reservation details
    def get(self, request, room_id):
        room = Room.objects.get(id=room_id)  # Retrieve the room by ID
        # Get reservations for today and future dates, ordered by date
        reservations = room.reservations.filter(date__gte=str(datetime.date.today())).order_by('date')
        return render(request, 'rooms/reservation.html', {'room': room, 'reservations': reservations})

    # Handle POST requests to process reservation form submission
    def post(self, request, room_id):
        room = Room.objects.get(id=room_id)  # Retrieve the room by ID
        date = request.POST.get('reservation-date')  # Get the reservation date
        comment = request.POST.get('comment')  # Get any comment associated with the reservation

        # Get reservations for today and future dates, ordered by date
        reservations = room.reservations.filter(date__gte=str(datetime.date.today())).order_by('date')

        # Validate reservation date
        if not date:
            return render(request, 'rooms/reservation.html',
                          context={'room': room, 'reservations': reservations, 'error': 'Reservation date is required.'})

        # Check if the room is already reserved for the selected date
        if Reservation.objects.filter(room=room, date=date):
            return render(request, 'rooms/reservation.html', context={'room': room, 'reservations': reservations, 'error': 'The room is already reserved'})

        reservation_date = datetime.datetime.strptime(date, "%Y-%m-%d").date()  # Convert string date to date object

        # Validate that the reservation date is not in the past
        if reservation_date < datetime.date.today():
            return render(request, 'rooms/reservation.html', context={'room': room, 'reservations': reservations, 'error': 'The date is in the past'})

        # Create a new reservation record in the database
        Reservation.objects.create(room=room, date=date, comment=comment)
        return redirect('rooms:room-list')  # Redirect to the list of rooms


# View for displaying detailed information about a room
class DetailRoomView(View):
    def get(self, request, room_id):
        room = Room.objects.get(id=room_id)  # Retrieve the room by ID
        # Get reservations for today and future dates, ordered by date
        reservations = room.reservations.filter(date__gte=str(datetime.date.today())).order_by('date')
        return render(request, 'rooms/detailed_view.html', context={'room': room, 'reservations': reservations})


# Function to show today's reservations
def today_reservation(request):
    today = datetime.date.today()  # Get today's date
    reservations = Reservation.objects.all()  # Retrieve all reservations

    context = {'reservations': reservations, 'today': today}  # Prepare context for rendering

    return render(request, 'rooms/rooms.html', context)  # Render the room list with today's reservations


# View for searching available rooms
class RoomSearchView(View):
    def get(self, request):
        rooms = Room.objects.all()  # Retrieve all rooms
        selected_capacity = request.GET.get('room_capacity', None)  # Get selected capacity from query parameters
        projector_available = request.GET.get('projector_available', None)  # Check if projector is available
        available_rooms = []  # List to store available rooms

        # Check if any filters are applied
        if selected_capacity or projector_available is not None:
            today = datetime.date.today()  # Get today's date
            # Get the IDs of rooms that are occupied today
            occupied_rooms = Reservation.objects.filter(date=today).values_list('room', flat=True)

            # Iterate through all rooms to apply filters
            for room in rooms:
                # Check capacity filter
                if selected_capacity and room.room_capacity < int(selected_capacity):
                    continue

                # Check projector availability filter
                if projector_available == 'on' and not room.projector_available:
                    continue

                # Check if the room is not occupied
                if room.id not in occupied_rooms:
                    available_rooms.append(room)  # Add room to available rooms list

        # Render the search results
        return render(request, 'rooms/search.html', {
            'rooms': rooms,
            'available_rooms': available_rooms,
            'projector_available': projector_available
        })

