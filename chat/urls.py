from django.urls import path
from .views import ChatHistoryView, ListChatRoomsView

urlpatterns = [
    path("chats/", ListChatRoomsView.as_view(), name="chats"),
    path("history/<str:room_name>/", ChatHistoryView.as_view(), name="chat-history"),
]
