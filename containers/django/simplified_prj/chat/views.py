from django.apps import apps
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.views.decorators.http import require_POST

from .models import Chat, Message, Dialogue, GroupChat


def get_player_chats_dict(player):
    dialogues = player.get_dialogues()
    g_chats = player.get_group_chats()
    chats = []
    for dialogue in dialogues:
        chats.append(dialogue.to_dict_authorised(player))
    for chat in g_chats:
        chats.append(chat.to_dict_authorised(player))
    return chats


@login_required
def my_chats_page(request):
    context = {'chats': get_player_chats_dict(request.user.player)}
    return render(request, 'chat/chats_page.html', context)


@login_required
def get_my_chats(request):
    return JsonResponse({'chats': get_player_chats_dict(request.user.player)})


@login_required
def get_my_dialogs(request):
    me = request.user.player
    dialogs = []
    for dialogue in me.get_dialogues():
        dialogs.append(dialogue.to_dict_authorised(me))
    return JsonResponse({'dialogs': dialogs})


@login_required
def get_my_group_chats(request):
    me = request.user.player
    group_chats = []
    for group_chat in me.get_group_chats():
        group_chats.append(group_chat.to_dict_authorised(me))
    return JsonResponse({'group_chats': group_chats})


def get_my_chat(request, chat_id):
    me = request.user.player
    chat = me.get_chat(chat_id)
    if chat == "Forbidden":
        return JsonResponse({'error': "Logged-in player is not in this chat"}, status=403)
    elif chat:
        try:
            dialogue = Dialogue.objects.get(pk=chat_id)
            print('>> Dialogue exists')
            return JsonResponse({'chat': dialogue.to_dict_authorised(request.user.player)})
        except Dialogue.DoesNotExist:
            print('>> Dialogue does NOT exist')
            g_chat = GroupChat.objects.get(pk=chat_id)
            return JsonResponse({'chat': g_chat.to_dict_authorised(request.user.player)})
    else:
        return JsonResponse({'error': "Chat with requested index not found"}, status=404)


@login_required
def get_messages_form_chat(request, chat_id):
    me = request.user.player
    chat = me.get_chat(chat_id)
    if chat == "Forbidden":
        return JsonResponse({'error': "Logged-in player is not in this chat"}, status=403)
    elif chat:
        dict_messages = []
        for msg in chat.get_messages():
            if chat.should_show_msg_from(msg.user.player, me):
                dict_messages.append(msg.to_dict())
        return JsonResponse({'messages': dict_messages})
    else:
        return JsonResponse({'error': "Chat with requested index not found"}, status=404)


@login_required
@require_POST
@csrf_protect
def post_message(request, chat_id):
    print("chat_id == ", chat_id)
    me = request.user.player
    chat = me.get_chat(chat_id)
    print('chat == ', chat)
    if chat == "Forbidden":
        return JsonResponse({'error': "Logged-in player is not in this chat"}, status=403)
    elif chat:
        print("request.body == ", request.body)
        body = request.body.decode('utf-8')
        if body:
            response = chat.can_post_message(me)
            if response['result'] == 'no':
                print('>>> Message NOT sent')
                return JsonResponse({'error': response['reason']}, status=403)
            else:
                message = Message.objects.create(user=me.user, chat=chat, content=body)
            return JsonResponse({'message': "Message sent successfully", 'id': message.id}, status=201)
        else:
            print('>>> Message NOT sent')
            return JsonResponse({'error': "Empty message body"}, status=400)
    else:
        print('>>> Chat NOT found')
        return JsonResponse({'error': "Chat with requested index not found"}, status=404)


@login_required
@require_POST
@csrf_protect
def leave_chat(request, chat_id):
    me = request.user.player
    chat = me.get_chat(chat_id)
    if chat == "Forbidden":
        return JsonResponse({'message': "Logged-in player is not in this chat"}, status=200)
    elif chat:
        try:
            Dialogue.objects.get(pk=chat_id)
            err_msg = ("Chat with requested id is a dialogue. It is impossible to leave the dialogue:"
                       "you can either block a player in this chat, and/or delete a dialogue explicitly.")
            return JsonResponse({'error': err_msg}, status=400)
        except Dialogue.DoesNotExist:
            g_chat = GroupChat.objects.get(pk=chat_id)
            if g_chat.admin.id == me.id:
                return JsonResponse({'error': "Logged-in player is an admin:"
                                              "admin can't leave a chat, only delete it"}, status=400)
            else:
                g_chat.players.remove(me)
                return JsonResponse({'message': 'You have successfully left the group chat.'}, status=201)
    else:
        return JsonResponse({'error': "Chat with requested index not found"}, status=404)


@login_required
@require_POST
@csrf_protect
def delete_chat(request, chat_id):
    print('In delete_chat')
    me = request.user.player
    chat = me.get_chat(chat_id)
    if chat == "Forbidden":
        return JsonResponse({'message': "Logged-in player is not in this chat"}, status=403)
    elif chat:
        try:
            dialogue = Dialogue.objects.get(pk=chat_id)
            dialogue.clear_messages()
            dialogue.delete()
            return JsonResponse({'message': 'Dialogue successfully deleted'}, status=201)
        except Dialogue.DoesNotExist:
            g_chat = GroupChat.objects.get(pk=chat_id)
            if g_chat.admin.id == me.id:
                g_chat.clear_messages()
                g_chat.delete()
                return JsonResponse({'message': 'GroupChat successfully deleted'}, status=201)
            else:
                return JsonResponse({'error': "Deleting GroupChat requires admin privilege"}, status=403)
    else:
        return JsonResponse({'error': "Chat with requested index not found"}, status=404)


@login_required
@require_POST
@csrf_protect
def block_player(request, chat_id, player_id):
    me = request.user.player
    chat = me.get_chat(chat_id)
    if chat == "Forbidden":
        return JsonResponse({'error': "Logged-in player is not in this chat"}, status=403)
    elif chat:
        try:
            Player = apps.get_model('mini_transcendence', 'Player')
            player = Player.objects.get(pk=player_id)
            try:
                Dialogue.objects.get(pk=chat_id)
                # chat with chat_id is a dialogue, not necessarily with particular player
                if me.has_player_in_blocklist(player):
                    return JsonResponse({'message': "player is already in the blocklist"}, status=200)
                else:
                    me.blocklist.add(player)
                    me.save()
            except Dialogue.DoesNotExist:
                g_chat = GroupChat.objects.get(pk=chat_id)
                if g_chat.admin.id == me.id:
                    if g_chat.blocked_players.filter(id=player_id).exists():
                        return JsonResponse({'message': "player is already in the blocklist"}, status=200)
                    else:
                        g_chat.blocked_players.add(player)
                        g_chat.save()
                        return JsonResponse({'message': 'GroupChat blocklist updated'}, status=201)
                else:
                    return JsonResponse({'error': "Blocking/unblocking players requires admin privilege"}, status=403)
        except Player.DoesNotExist:
            return JsonResponse({'error': "Player with requested index not found"}, status=404)
    else:
        return JsonResponse({'error': "Chat with requested index not found"}, status=404)


@login_required
@require_POST
@csrf_protect
def unblock_player(request, chat_id, player_id):
    me = request.user.player
    chat = me.get_chat(chat_id)
    if chat == "Forbidden":
        return JsonResponse({'message': "Logged-in player is not in this chat"}, status=403)
    elif chat:
        try:
            Player = apps.get_model('mini_transcendence', 'Player')
            player = Player.objects.get(pk=player_id)
            try:
                Dialogue.objects.get(pk=chat_id)
                # chat with chat_id is a dialogue, not necessarily with particular player
                if me.has_player_in_blocklist(player):
                    me.blocklist.remove(player)
                    me.save()
                else:
                    return JsonResponse({'message': "player was not listed in your blocklist"}, status=200)
            except Dialogue.DoesNotExist:
                g_chat = GroupChat.objects.get(pk=chat_id)
                if g_chat.admin.id == me.id:
                    if g_chat.blocked_players.filter(id=player_id).exists():
                        g_chat.blocked_players.remove(player)
                        g_chat.save()
                        return JsonResponse({'message': 'GroupChat blocklist updated'}, status=201)
                    else:
                        return JsonResponse({'message': "player is already in the blocklist"}, status=200)
                else:
                    return JsonResponse({'error': "Blocking/unblocking players requires admin privilege"}, status=403)
        except Player.DoesNotExist:
            return JsonResponse({'error': "Player with requested index not found"}, status=404)
    else:
        return JsonResponse({'error': "Chat with requested index not found"}, status=404)


@login_required
@require_POST
@csrf_protect
def invite_player(request, chat_id, player_id):
    me = request.user.player
    chat = me.get_chat(chat_id)
    if chat == "Forbidden":
        return JsonResponse({'message': "Logged-in player is not in this chat"}, status=403)
    elif chat:
        try:
            Player = apps.get_model('mini_transcendence', 'Player')
            player = Player.objects.get(pk=player_id)
            try:
                Dialogue.objects.get(pk=chat_id)
                return JsonResponse({'error': "chat with provided id is an existing dialogue."
                                              "Players can't be added or removed from it."}, status=403)
            except Dialogue.DoesNotExist:
                g_chat = GroupChat.objects.get(pk=chat_id)
                if g_chat.admin.id == me.id:
                    if g_chat.players.filter(id=player_id).exists():
                        return JsonResponse({'message': "player is already a member of this chat"}, status=200)
                    else:
                        g_chat.players.add(player)
                        g_chat.save()
                        return JsonResponse({'message': "new player added to the chat"}, status=201)
                else:
                    return JsonResponse({'error': "Adding new players requires admin privilege"}, status=403)
        except Player.DoesNotExist:
            return JsonResponse({'error': "Player with requested index not found"}, status=404)
    else:
        return JsonResponse({'error': "Chat with requested index not found"}, status=404)


@login_required
@require_POST
@csrf_protect
def remove_player(request, chat_id, player_id):
    me = request.user.player
    chat = me.get_chat(chat_id)
    if chat == "Forbidden":
        return JsonResponse({'message': "Logged-in player is not in this chat"}, status=403)
    elif chat:
        try:
            Player = apps.get_model('mini_transcendence', 'Player')
            player = Player.objects.get(pk=player_id)
            try:
                Dialogue.objects.get(pk=chat_id)
                return JsonResponse({'error': "chat with provided id is an existing dialogue."
                                              "Players can't be added or removed from it."}, status=403)
            except Dialogue.DoesNotExist:
                g_chat = GroupChat.objects.get(pk=chat_id)
                if g_chat.admin.id == me.id:
                    if g_chat.players.filter(id=player_id).exists():
                        g_chat.players.remove(player)
                        g_chat.save()
                        return JsonResponse({'message': "player removed from the chat"}, status=201)
                    else:
                        return JsonResponse({'message': "player is not a member of this chat"}, status=200)
                else:
                    return JsonResponse({'error': "Adding new players requires admin privilege"}, status=403)
        except Player.DoesNotExist:
            return JsonResponse({'error': "Player with requested index not found"}, status=404)
    else:
        return JsonResponse({'error': "Chat with requested index not found"}, status=404)
