from django.urls import path


from .views import RoomListView, AddRoomView, DeleteRoomView, RoomModifyView, ReservationView, DetailRoomView, \
    RoomSearchView

app_name = 'rooms'

#addresses to subpages
urlpatterns = [
    path('room/new/', AddRoomView.as_view(), name="add-room"),
    path('', RoomListView.as_view(), name='room-list'),
    path('room/delete/<int:room_id>/', DeleteRoomView.as_view(), name="delete-room"),
    path('room/modify/<int:id>/', RoomModifyView.as_view(), name="update-room"),
    path('room/reserve/<int:room_id>', ReservationView.as_view(), name='reservation'),
    path('room/detail/<int:room_id>/', DetailRoomView.as_view(), name='room-detail'),
    path('room/search/', RoomSearchView.as_view(), name='room-search')
]
