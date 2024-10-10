from django.urls import path

from . import views
from .views import RoomListView, AddRoomView, DeleteRoomView, RoomModifyView

app_name = 'rooms'

urlpatterns = [
    path('room/new/', AddRoomView.as_view(), name="add-room"),
    path('', RoomListView.as_view(), name='room-list'),
    path('room/delete/<int:room_id>/', DeleteRoomView.as_view(), name="delete-room"),
    path('room/modify/<int:id>/', RoomModifyView.as_view(), name="update-room")
]
