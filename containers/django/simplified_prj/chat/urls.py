from django.urls import path
from . import views

urlpatterns = [
    path('', views.my_chats_page, name='my-chats'),
    # Retrieve info
    path('api/my/all/', views.get_my_chats, name='get-my-chats'),
    path('api/my/dialogs/', views.get_my_dialogs, name='get-my-dialogues'),
    path('api/my/group-chats/', views.get_my_group_chats, name='get-my-group-chats'),
    path('api/my/<int:chat_id>/', views.get_my_chat, name='get-my-chat'),
    path('api/<int:chat_id>/messages/', views.get_messages_form_chat, name='get-messages-form-chat'),
    # Perform action
    path('api/<int:chat_id>/messages/send/', views.post_message, name='post-message'),
    path('api/<int:chat_id>/leave/', views.leave_chat, name='leave-chat'),
    path('api/<int:chat_id>/delete/', views.delete_chat, name='delete-chat'),
    path('api/<int:chat_id>/block/<int:player_id>', views.block_player, name='block-player'),
    path('api/<int:chat_id>/unblock/<int:player_id>', views.unblock_player, name='unblock-player'),
    path('api/<int:chat_id>/invite/<int:player_id>', views.invite_player, name='invite-player'),
    path('api/<int:chat_id>/remove/<int:player_id>', views.remove_player, name='remove-player'),
]
