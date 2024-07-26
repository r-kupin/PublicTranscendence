
# Test users

| login    | password |
|----------|----------|
| rokupin  | lg4uf4rz |
| anvincen | i9fd0y5n |
| admin    | i34dnfen |
| bobr     | i34dnfen |
| silent   | i34dnfen |

# API
## Player
### GET
These views are read-only. Should be only made with a *GET* request.

| url                                                        | Django tag                                       | Sign In required |
| ---------------------------------------------------------- | ------------------------------------------------ | ---------------- |
| [api/players/me/](#get-my-info)                            | `{% url 'players:get-my-info' %}`                | ✅                |
| [api/players/all/](#list)                                  | `{% url 'all-players:list' %}`                   | ❌                |
| [api/players/me/{player_id}/](#get-related-player-info)    | `{% url 'players:get-related-player-info' id %}` | ✅                |
| [api/players/all/except-me/](#except-me)                   | `{% url 'all-players:except-me' %}`              | ✅                |
| [api/players/all/online/](#online)                         | `{% url 'all-players:online' %}`                 | ❌                |
| [api/players/all/online/except-me/](#online-except-me)     | `{% url 'all-players:online-except-me' %}`       | ✅                |
| [api/players/{player_id}/](#get-player-info)               | `{% url 'players:get-player-info' id %}`         | ❌                |
| [api/players/{player_id}/actions/](#get-available-actions) | `{% url 'players:get-available-actions' id %}`   | ✅                |
#### get-my-info  
Logged-in player's info. Example:  
```json  
{
  "player": {
    "id": 4,
    "username": "rokupin",
    "games": 2,
    "wins": 112,
    "loses": 120,
    "avatar_url": "/media/avatars/rokupin_zt8ss8y.jpg",
    "records": [
      "/game/api/records/get/2/",
      "/game/api/records/get/3/",
      "/game/api/records/get/4/",
      "/game/api/records/get/7/"
    ],
    "friendlist": [
      "/api/players/me/5/",
      "/api/players/me/6/"
    ],
    "blocklist": [],
    "tournament_stats": [
      "/game/api/tournament/records/3/player/4",
      "/game/api/tournament/records/4/player/4",
      "/game/api/tournament/records/5/player/4"
    ],
    "intra_login": "rokupin",
    "chats_link": "/chat/api/my/all/"
  }
}  
```
#### list
All `Player` instances, represented in a same way as [get-my-info](#get-my-info)  Example:
```json
{
   "players":[
      {
         "id":4,
         "username":"rokupin",
         "games":2,
         "wins":112,
         "loses":120,
         "avatar_url":"/media/avatars/rokupin_zt8ss8y.jpg",
         "records":[
            "/game/api/records/get/2/",
            "/game/api/records/get/3/",
            "/game/api/records/get/4/",
            "/game/api/records/get/7/"
         ],
         "friendlist":[
            "/api/players/me/5/",
            "/api/players/me/6/"
         ],
         "blocklist":[
            
         ],
         "tournament_stats":[
            "/game/api/tournament/records/3/player/4",
            "/game/api/tournament/records/4/player/4",
            "/game/api/tournament/records/5/player/4"
         ],
         "intra_login":"rokupin",
         "chats_link":"/chat/api/my/all/"
      }, 
	  {
        
      }
   ]
}
```

#### get-related-player-info
Like [get-player-info](#get-player-info) but with some relative data:
- **friend** & **blocked**: checks the **friendlist**s and **blocklist**s of both players
- **actions_link**: Link to the list of the available [actions](#get-available-actions) 
- **has_dialogue_with_me**: Link to dialogue between *logged-in player* and *other player*, if it exists
```json
{
  "player": {
    "id": 5,
    "username": "anvincen",
    "games": 2,
    "wins": 135,
    "loses": 85,
    "avatar_url": "/media/avatars/anvin.jpeg",
    "records": [
      "/game/api/records/get/2/",
      "/game/api/records/get/3/",
      "/game/api/records/get/4/",
      "/game/api/records/get/5/",
      "/game/api/records/get/6/",
      "/game/api/records/get/9/",
      "/game/api/records/get/11/",
    ],
    "friendlist": [
      "/api/players/me/6/"
    ],
    "blocklist": [],
    "tournament_stats": [
      "/game/api/tournament/records/3/player/5",
      "/game/api/tournament/records/4/player/5",
      "/game/api/tournament/records/5/player/5"
    ],
    "intra_login": "anvincen",
    "i_am_his_friend": false,
    "he_is_my_friend": true,
    "i_am_blocked": false,
    "he_is_blocked": false,
    "actions_link": "/api/players/5/actions/",
    "has_dialogue_with_me": "/chat/api/my/126/"
  }
}
```
#### except-me
Like [list](#list), but logged-in player is not present in the list, and all `player` elements are with [relative data](#get-related-player-info).
#### online
Same as [list](#list) but showing only players currently online:
```json
{
   "online_players":[
      {
         
      }
   ]
}
```
#### online-except-me
Same as [except-me](#except-me) but showing only online players.
#### get-player-info
Like [get-my-info](#get-my-info) but for the player with specified **id**, and without `"chats_link"` key.
#### get-available-actions
List of available actions that *logged-in player* can perform on *other player*, who is identified by the **id**.
##### If *other player* is *logged-in player*
```json
{
   "actions":{
      "get_player_data":"/api/players/me/"
   }
}
```
##### If *other player* (id=5) is in the friend-list of the *logged-in player*
```json
{
   "actions":{
      "get_player_data":"/api/players/me/5/",
	  "invite_for_match":"/game/api/match/invite/5/",
      "remove_from_friendlist":"/api/players/5/remove-friend/"
   }
}
```
##### If *other player* (id=5) is NOT the friend-list of the *logged-in player*
```json
{
   "actions":{
      "get_player_data":"/api/players/me/5/",
	  "invite_for_match":"/game/api/match/invite/5/",
      "add_to_friendlist":"/api/players/5/add-friend/"
   }
}
```
##### If *other player* (id=5) has a dialogue with the *logged-in player*
```json
{
   "actions":{
      "get_player_data":"/api/players/me/5/",
	  "invite_for_match":"/game/api/match/invite/5/",
      "goto_dialogue":"/chat/api/4/",
      "remove_dialogue":"/api/players/5/remove-dialogue/"
   }
}
```
##### If *other player* (id=5) has NO dialogue with the *logged-in player*
Action to the link is yet to be implemented
```json
{
   "actions":{
      "get_player_data":"/api/players/me/5/",
	  "invite_for_match":"/game/api/match/invite/5/",
      "create_dialogue":"/api/players/5/create-dialogue/"
   }
}
```
### POST
These views are intended to modify logged-in `Player`'s relationships with other players.
Should be only made with a *POST* request, and don't forget `{% csrf_token %}` - without it django won't process post request and return **403**.

| url                                      | Django tag                                             | Sign In required |
|------------------------------------------|--------------------------------------------------------|------------------|
| api/players/{player_id}/add-friend/      | `{% url 'players-action:add-to-friendlist' id %}`      | ✅                |
| api/players/{player_id}/remove-friend/   | `{% url 'players-action:remove-from-friendlist' id %}` | ✅                |
| api/players/{player_id}/remove-dialogue/ | `{% url 'players-action:remove-dialogue' id %}`        | ✅                |
| api/players/{player_id}/create-dialogue/ | `{% url 'players-action:create-dialogue' id %}`        | ✅                |
| api/players/{player_id}/unblock/         | `{% url 'players-action:unblock-player' id %}`         | ✅                |
| api/players/{player_id}/block/           | `{% url 'players-action:block-player' id %}`           | ✅                |

All of those actions share similar behavior:
- **Request is not `POST`**: returns **400** and `{'error': 'Invalid request'}` as response's body
- **Player with given id doesn't exist**: returns **404**
- **Action is impossible to perform** (such as block yourself): returns **400** and `{'error': "Can't block myself"}`
- **Result of performed action is already in place** (such as add to friend-list a player that is already there): returns **200** and `{'message': "already in the friendlist"}`
- **Action performed successfully**: returns **201**

## Game

| url                                                   | Sign In required | Method |
|-------------------------------------------------------| ---------------- | ------ |
| [game/api/records/get/{record_id}/](#get-record-info) | ❌                | GET    |
| [game/api/match/invite/{player_id}/](#invite)         | ✅                | POST   |
| [game/api/match/accept/{game_id}/](#accept)           | ✅                | POST   |
| [game/api/match/proceed/{game_id}/](#proceed)         | ✅                | POST   |
| [game/api/match/decline/{game_id}/](#decline)         | ✅                | POST   |

### GET
#### get-record-info
Example:
```json
{
   "record":{
      "id":1,
      "player1_score":0,
      "player2_score":2,
      "player1_username":"rokupin",
      "player2_username":"anvincen",
      "player1_link":"/api/players/4/",
      "player2_link":"/api/players/5/",
      "timestamp":"2024-05-23T14:37:29.700",
      "winner":"anvincen"
   }
}
```
"winner" key will not be present if score is equal or match was not finished 
### POST
All actions return JSON response alike:
```json
{"message": "..."}
```
is action was successful, or
```json
{"error": "..."}
```
otherwise.
#### invite
Creates the instance of the game and sends invitation via a specific message in the Dialogue with invited player.
##### invite successful
Message contents:
```json
{
      "sender_username": "rokupin",
      "sender_link": "/api/players/4/",
      "chat": "/chat/api/my/7/",
      "content": "You are invited to a match!",
      "type": "invite_received",
      "timestamp": "2024-06-27T05:10:02.711",
      "actions": {
        "accept_link": "/game/api/match/accept/0756e3d6-e9fa-4b7f-8a30-5dd4b5e7779c/",
        "decline_link": "/game/api/match/decline/0756e3d6-e9fa-4b7f-8a30-5dd4b5e7779c/"
      }
}
```
Response, sent back:
```json
{
      "message": "Invitation sent successfully",
      "game_id": "08e3091d-e982-41a8-b86f-46d58e010ce2"
}  
```
##### invite failed
In this case message won't be sent, but response with explanations will be returned.
Reasons might be:
- Invited player not found
- Invited player blocked you or is blocked by you 
#### accept
Marks invitation as accepted, sends a specific confirmation message to the Dialog.
##### accept successful
Message contents:
```json
    {
      "sender_username": "anvincen",
      "sender_link": "/api/players/5/",
      "chat": "/chat/api/my/7/",
      "content": "Your invite is accepted!",
      "type": "invite_accepted",
      "timestamp": "2024-06-27T05:12:26.083",
      "actions": {
        "proceed_link": "/game/api/match/proceed/0756e3d6-e9fa-4b7f-8a30-5dd4b5e7779c/"
      }
    }
```
As a response client receives  gaming page itself.
##### accept failed
In this case message won't be sent, but response with explanations will be returned.
Reasons might be:
- Game with given id not found
- Logged-in player is not the one, who was invited
- Player who sent invitation is not found
- Attempt to accept already accepted invite
#### proceed
Leads match initiator to the gaming page.
If operation failed - response with explanations will be returned.
Reasons might be:
- Game with given id not found
- Player to whom the invitation was sent is not found
- Invited player had not accepted invitation
#### decline
Let's client do decline the invitation. On success, sends message to the Dialogue. 
##### decline successful
Message contents: 
```json
{
      "sender_username": "anvincen",
      "sender_link": "/api/players/5/",
      "chat": "/chat/api/my/7/",
      "content": "Your invite was declined!",
      "type": "invite_declined",
      "timestamp": "2024-07-12T12:02:23.317"
}
```
### ws/game/{game_id}/
By opening of the web socket on this address - django creates consumer that will communicate player's actions to the game engine running on the server side during the match.
#### Readiness report
**client -> Django**
When client is ready to start actually playing, it sends to the socket:
```json
{  
  "type":"report_ready"  
}
```
#### Game starts
**Django -> client**
When all players reported ready Django launches the game and sends message to all clients:
```json
{  
  "type":"game_starts"  
}
```
So clients can load gaming field.
#### State update
**Django -> client**

Whenever state of the game is changed, be it:
- ball position change
- paddle position of any of the player change
- score change

Django sends message like this to both clients, so they can re-render their gaming space
##### simple game
```json
{  
  "type": "game_state_update",  
  "state": {  
    "initiator_id": 5,  
    "invited_id": 4,  
    "initiator_score": 2,  
    "invited_score": 2,  
    "initiator_paddle_y": 210,  
    "invited_paddle_y": 210,  
    "ball_position_x": 570.0483101720062,  
    "ball_position_y": 217.2525323880484,  
    "ball_direction_y": 0.43745130022983614,  
    "ball_direction_x": 0.5625486997701639,
    "tournament": false
  }  
}
```
##### tournament match
If the game is a tournament match - django also adds time counter, that lets players know how much time do they have before the tier ends:
```json
{  
  "type": "game_state_update",  
  "state": {  
    "initiator_id": 5,  
    "invited_id": 4,  
    "initiator_score": 2,  
    "invited_score": 2,  
    "initiator_paddle_y": 210,  
    "invited_paddle_y": 210,  
    "ball_position_x": 570.0483101720062,  
    "ball_position_y": 217.2525323880484,  
    "ball_direction_y": 0.43745130022983614,  
    "ball_direction_x": 0.5625486997701639,
    "tournament": true,
    "minutes_left": 9,
	"seconds_left": 29
  }  
}
```
#### Client's action report
**client -> Django**
##### Paddle update
When client moves it's paddle - it should send message like:
```json
{  
  "type": "paddle_position_update",  
  "position": 217.2525323880484
}
```
##### Unfinished match stop
To stop match before it's ended client should send:
```json
{  
  "type": "report_left"
}
```
Which will stop the match
##### Disconnect
On disconnect server acts in the same way as on **unfinished match stop**
#### Game end
**Django -> client**

Game ends when:
- One of the players scored 5 goals
- One of the players is disconnected or stopped the game

Then Django sends to all connected players following message:
```json
{  
    "type": "game_ended",  
    "initiator_score": 0,  
    "invited_score": 5  
}
```

## Tournament
| url                                                   | Sign In required | Method |
|-------------------------------------------------------| ---------------- | ------ |
| [game/api/tournament/create/](#create-tournament)               | ✅                | POST   |
| [game/api/tournament/subscribe/](#subscribe-tournament)            | ✅                | POST   |

#### create-tournament
By posting to this link Player might propose a tournament.  Request's body should be a valid JSON dictionary and contain a timestamp that's at least 1 minute in the future. Before that point players are able to subscribe to the tournament. After - tournament would create match lists.
Also, it is possible to specify an alias - nickname displayed during tournament.
Only 1 tournament might exist at any time.
Timestamp example:
```json
{
      "starts_at": "2024-07-12T12:02:23.317",
      "tournament_alias": "tournament_alias"
}
```
Responses:
- **200**: `message` Tournament exists
- **201**: `message` Created successfully
- **400**: `error` Incorrect body
The creation of the tournament involves the following steps:
1. Each existing player who can communicate with the one who created tournament receives in the dialogue a specific message proposing to subscribe for a tournament. Link is only active before the specified timestamp.
```json
{
      "sender_username": "rokupin",
      "sender_link": "/api/players/4/",
      "chat": "/chat/api/my/24/",
      "content": "The tournament will start at 11:00 AM. Subscribe, while it`s not too late",
      "type": "tournament_subscription_invite",
      "timestamp": "2024-07-17T08:58:04.092Z",
      "actions": {
        "subscribe_link": "/game/api/tournament/subscribe/"
      }
}
```
2. New GroupChat by the name `{player.username}'s tournament` get's created. If chat already exists - the old one gets deleted.
3. Tournament instance waits while time reaches **starts_at** timestamp
4. After that - In the group chat Tournament posts messages announcing current tier and links for the matches for that tier. Let's say - tournament was created by *rokupin* and the subscribed players were *anvincen* and *bobr*. By clicking `proceed_link` *rokupin* and *anvincen* will be redirected to the gaming page (no need to accept), *bobr* will get an error.
```json
[
    {
      "sender_username": "rokupin",
      "sender_link": "/api/players/4/",
      "chat": "/chat/api/my/73/",
      "content": "Tier 0 matches are ready!",
      "type": "message",
      "timestamp": "2024-07-17T09:00:00.170Z"
    },
    {
      "sender_username": "rokupin",
      "sender_link": "/api/players/4/",
      "chat": "/chat/api/my/73/",
      "content": "rokupin vs anvincen",
      "type": "tournament_match_invite",
      "timestamp": "2024-07-17T09:00:00.177Z",
      "actions": {
        "proceed_link": "/game/api/match/proceed/2fa5cae2-d515-4993-ae83-2a2c5d6d364a/"
      }
    }
]
```
5. Tournament waits until all games in the tier are played or while 10 minunes cap expires.
	1. If no GameRecords were submitted in 10 minute period - tournament interrupts, no tournament records are created
	2. If only one game record was submitted - the winner of that match becomes a winner of the tournament.
	3. Else - matchmaking system announces next tier - taking winners from previous tier and player, who had no pair to play with, players who lost are removed from `players_set`. Assume, that *rokupin* won against *anvincen:*
```json
{
      "sender_username": "rokupin",
      "sender_link": "/api/players/4/",
      "chat": "/chat/api/my/73/",
      "content": "Tier 1 matches are ready!",
      "type": "message",
      "timestamp": "2024-07-17T09:16:23.298Z"
    },
    {
      "sender_username": "rokupin",
      "sender_link": "/api/players/4/",
      "chat": "/chat/api/my/73/",
      "content": "rokupin vs bobr",
      "type": "tournament_match_invite",
      "timestamp": "2024-07-17T09:16:37.074Z",
      "actions": {
        "proceed_link": "/game/api/match/proceed/3ed09d0c-e965-45ce-ac09-9f25f682b37a/"
      }
}
```
6. Last player left in the `players_set` wins the tournament.
#### subscribe-tournament
By clicking this link player get's added to this tournament's `players_set` and to the tournament's GroupChat. Optionally, player can specify tournament alias:
```json
{
      "tournament_alias": "tournament_alias"
}
```


## Chat
There are 2 types of chats:
- *Dialogue*:
	- Always has only *player1* and *player2* in it
	- Each player can block another player via his own blocklist
	- Name is generated dynamically. If *player1* is viewing the chat - the name of it will be: *Me with player2* and the same in reverse.
- *GroupChat*
	- Has a *name* field
	- May host indefinite amount of players
	- Has *admin* player
### GET

| url                                                     | Django tag                              | Sign In required |
|---------------------------------------------------------| --------------------------------------- | ---------------- |
| [chat/api/my/all/](#get-my-chats)                       | `{% url 'get-my-chats' %}`              | ✅                |
| [chat/api/my/dialogs/](#get-my-dialogues)               | `{% url 'get-my-dialogues' %}`          | ✅                |
| [chat/api/my/group-chats/](#get-my-group-chats)         | `{% url 'get-my-group-chats' %}`        | ✅                |
| [chat/api/my/{chat_id}/](#get-my-chat)                  | `{% url 'get-my-chat' id %}`            | ✅                |
| [chat/api/{chat_id}/messages/](#get-messages-form-chat) | `{% url 'get-messages-form-chat' id %}` | ✅                |
#### get-my-chats
List of all chats in which current player takes part. Each particular chat will be explained below:
```json
{
   "chats":[
      {
         "chat_id":2,
         "created_at":"2024-06-11T09:06:07.720",
         "link_to_messages":"/chat/api/2/messages/",
         "players_in_chat":[
            {
               "username":"anvincen",
               "link":"/api/players/me/5/",
               "is_blocked":false,
               "block":"/api/players/5/block/"
            }
         ],
         "i_am_blocked":false,
         "type":"Dialogue",
         "name":"Me with anvincen",
         "players_amount":1,
         "action_links":{
            "post_message":"/chat/api/2/messages/send/",
            "delete_chat":"/api/players/4/remove-dialogue/"
         }
      },
      {
         "chat_id":4,
         "created_at":"2024-06-15T11:56:27.018",
         "link_to_messages":"/chat/api/4/messages/",
         "players_in_chat":[
            {
               "username":"bobr",
               "link":"/api/players/me/6/",
               "is_blocked":true,
               "unblock":"/api/players/6/unblock/"
            }
         ],
         "i_am_blocked":false,
         "type":"Dialogue",
         "name":"Me with bobr",
         "players_amount":1,
         "action_links":{
            "post_message":"/chat/api/4/messages/send/",
            "delete_chat":"/api/players/4/remove-dialogue/"
         }
      },
      {
         "chat_id":3,
         "created_at":"2024-06-11T09:11:28.619",
         "link_to_messages":"/chat/api/3/messages/",
         "players_in_chat":[
            {
               "username":"anvincen",
               "link":"/api/players/me/5/",
               "is_blocked":true,
               "is_admin":false
            },
            {
               "username":"bobr",
               "link":"/api/players/me/6/",
               "is_blocked":false,
               "is_admin":true
            }
         ],
         "type":"GroupChat",
         "name":"Chatty BoBr",
         "i_am_blocked":false,
         "players_amount":2,
         "action_links":{
            "post_message":"/chat/api/3/messages/send/",
            "leave_chat":"/chat/api/3/leave/"
         },
         "i_am_admin":false,
         "admin":{
            "username":"bobr",
            "link":"/api/players/me/6/"
         }
      },
      {
         "chat_id":5,
         "created_at":"2024-06-16T09:03:08.174",
         "link_to_messages":"/chat/api/5/messages/",
         "players_in_chat":[
            {
               "username":"anvincen",
               "link":"/api/players/me/5/",
               "is_blocked":false,
               "is_admin":false,
               "block":"/chat/api/5/block/5",
               "remove":"/chat/api/5/remove/5"
            },
            {
               "username":"bobr",
               "link":"/api/players/me/6/",
               "is_blocked":true,
               "is_admin":false,
               "unblock":"/chat/api/5/unblock/6",
               "remove":"/chat/api/5/remove/6"
            }
         ],
         "type":"GroupChat",
         "name":"Rokupin's chat",
         "i_am_blocked":false,
         "players_amount":2,
         "action_links":{
            "post_message":"/chat/api/5/messages/send/",
            "delete_chat":"/chat/api/5/delete/"
         },
         "i_am_admin":true
      }
   ]
}
```
#### get-my-dialogues
Retrieves all dialogues associated with logged-in user.
```json
{
   "dialogs":[
      {
         "chat_id":2,
         "created_at":"2024-06-11T09:06:07.720",
         "link_to_messages":"/chat/api/2/messages/",
         "players_in_chat":[
            {
               "username":"anvincen",
               "link":"/api/players/me/5/",
               "is_blocked":false,
               "block":"/api/players/5/block/"
            }
         ],
         "i_am_blocked":false,
         "type":"Dialogue",
         "name":"Me with anvincen",
         "players_amount":1,
         "action_links":{
            "post_message":"/chat/api/2/messages/send/",
            "delete_chat":"/api/players/4/remove-dialogue/"
         }
      },
      {
         "chat_id":4,
         "created_at":"2024-06-15T11:56:27.018",
         "link_to_messages":"/chat/api/4/messages/",
         "players_in_chat":[
            {
               "username":"bobr",
               "link":"/api/players/me/6/",
               "is_blocked":true,
               "unblock":"/api/players/6/unblock/"
            }
         ],
         "i_am_blocked":false,
         "type":"Dialogue",
         "name":"Me with bobr",
         "players_amount":1,
         "action_links":{
            "post_message":"/chat/api/4/messages/send/",
            "delete_chat":"/api/players/4/remove-dialogue/"
         }
      }
   ]
}
```
##### players_in_chat
Iterable list of players. In a dialogue there will always be only element.
- `is_blocked` and `block`/`unblock` elements are related to logged-in player's **blocklist**
- `i_am_blocked` represent's presence of logged-in player in the **blocklist** of his dialog partner.
##### action_links
It is impossible to *leave* a dialogue. Each participant has a choice: either *block* another participant or *delete* the chat. When chat is deleted - all messages associated are deleted too.
#### get-my-group-chats
Retrieves all GroupChats associated with logged-in user.
```json
{
   "group_chats":[
      {
         "chat_id":3,
         "created_at":"2024-06-11T09:11:28.619",
         "link_to_messages":"/chat/api/3/messages/",
         "players_in_chat":[
            {
               "username":"anvincen",
               "link":"/api/players/me/5/",
               "is_blocked":true,
               "is_admin":false
            },
            {
               "username":"bobr",
               "link":"/api/players/me/6/",
               "is_blocked":false,
               "is_admin":true
            }
         ],
         "type":"GroupChat",
         "name":"Chatty BoBr",
         "i_am_blocked":false,
         "players_amount":2,
         "action_links":{
            "post_message":"/chat/api/3/messages/send/",
            "leave_chat":"/chat/api/3/leave/"
         },
         "i_am_admin":false,
         "admin":{
            "username":"bobr",
            "link":"/api/players/me/6/"
         }
      },
      {
         "chat_id":5,
         "created_at":"2024-06-16T09:03:08.174",
         "link_to_messages":"/chat/api/5/messages/",
         "players_in_chat":[
            {
               "username":"anvincen",
               "link":"/api/players/me/5/",
               "is_blocked":false,
               "is_admin":false,
               "block":"/chat/api/5/block/5",
               "remove":"/chat/api/5/remove/5"
            },
            {
               "username":"bobr",
               "link":"/api/players/me/6/",
               "is_blocked":true,
               "is_admin":false,
               "unblock":"/chat/api/5/unblock/6",
               "remove":"/chat/api/5/remove/6"
            }
         ],
         "type":"GroupChat",
         "name":"Rokupin's chat",
         "i_am_blocked":false,
         "players_amount":2,
         "action_links":{
            "post_message":"/chat/api/5/messages/send/",
            "delete_chat":"/chat/api/5/delete/"
         },
         "i_am_admin":true
      }
   ]
}
```
##### players_in_chat
Iterable list of players. In a GroupChat might be from zero (only logged-in player) to the infinite.
- `is_blocked` and `block`/`unblock` elements are related to this GroupChat's **blocklist**. Only *admin* player of this chat can see and use `block`/`unblock` links.
- `remove` - another *admin*'s action, removes player from chat participants list.
##### action_links
Non-admin player might `leave_chat`, while admin can only `delete_chat`
#### get-my-chat
Returns a chat in which logged-in player participates. 
- If requested chat doesn't exist - returns *404*
- If logged-in player takes no part in found chat - returns *403*
- If all went fine - returns `{chat: { ... }}` JSON
#### get-messages-form-chat
Returns list of messages related to the chat with **id**. Format is the same, regardless of whether the chat type.
##### Dialogue:
1. **invite_received**: message with this type is sent to the player who is invited to play a gamefrom the one, who invites
2. **invite_accepted**: sent to the player who initiated the match if invited player accepted that invite
3. **tournament_subscription_invite**: sent by the player who created the tournament to all players present in the system, except the blocked ones
4. **message**: just a generic text message
```json
{
  "messages": [
    {
      "sender_username": "rokupin",
      "sender_link": "/api/players/4/",
      "chat": "/chat/api/my/7/",
      "content": "You are invited to a match!",
      "type": "invite_received",
      "timestamp": "2024-06-27T05:10:02.711",
      "actions": {
        "accept_link": "/game/api/match/accept/0756e3d6-e9fa-4b7f-8a30-5dd4b5e7779c/",
        "decline_link": "/game/api/match/decline/0756e3d6-e9fa-4b7f-8a30-5dd4b5e7779c/"
      }
    },
    {
      "sender_username": "anvincen",
      "sender_link": "/api/players/5/",
      "chat": "/chat/api/my/7/",
      "content": "Your invite is accepted!",
      "type": "invite_accepted",
      "timestamp": "2024-06-27T05:12:26.083",
      "actions": {
        "proceed_link": "/game/api/match/proceed/0756e3d6-e9fa-4b7f-8a30-5dd4b5e7779c/"
      }
    },
	{
      "sender_username": "rokupin",
      "sender_link": "/api/players/1/",
      "chat": "/chat/api/my/2/",
      "content": "The tournament will start at 04:08 PM. Subscribe, while it`s not too late",
      "type": "tournament_subscription_invite",
      "timestamp": "2024-07-25T14:06:20.170Z",
      "actions": {
        "subscribe_link": "/game/api/tournament/subscribe/"
      }
    },
    {
      "sender_username": "rokupin",
      "sender_link": "/api/players/4/",
      "chat": "/chat/api/my/7/",
      "content": "Hello, World!",
      "type": "message",
      "timestamp": "2024-06-27T05:21:29.401"
    }
  ]
}
```
4. **invite_declined**: sent to the player who initiated the match if invited player rejected that invite
```json
{
  "messages": [
    {
      "sender_username": "rokupin",
      "sender_link": "/api/players/4/",
      "chat": "/chat/api/my/4/",
      "content": "You are invited to a match!",
      "type": "invite_received",
      "timestamp": "2024-06-27T05:13:12.867",
      "actions": {
        "accept_link": "/game/api/match/accept/78a88b1c-d423-4855-b495-817bd96383f9/",
        "decline_link": "/game/api/match/decline/78a88b1c-d423-4855-b495-817bd96383f9/"
      }
    },
    {
      "sender_username": "bobr",
      "sender_link": "/api/players/6/",
      "chat": "/chat/api/my/4/",
      "content": "Your invite wad declined!",
      "type": "invite_declined",
      "timestamp": "2024-06-27T05:16:53.930"
    }
  ]
}
```
##### GroupChat:
**tournament_match_invite**: message posted by the player who created the tournament in the tournament chat. When tournament matches are ready to play - messages of this type will invite players to play.
```json
{
  "messages": [
    {
      "sender_username": "toto",
      "sender_link": "/api/players/2/",
      "chat": "/chat/api/my/3/",
      "content": "Tier 0 matches are ready!",
      "type": "message",
      "timestamp": "2024-07-25T14:12:31.909Z"
    },
    {
      "sender_username": "toto",
      "sender_link": "/api/players/2/",
      "chat": "/chat/api/my/3/",
      "content": "rokupin VS toto",
      "type": "tournament_match_invite",
      "timestamp": "2024-07-25T14:12:31.943Z",
      "actions": {
        "proceed_link": "/game/api/match/proceed/0a5f4ef8-65aa-4875-a5c6-d43cda287fc3/"
      }
    },
    {
      "sender_username": "toto",
      "sender_link": "/api/players/2/",
      "chat": "/chat/api/my/3/",
      "content": "You have 10 minutes to finish your match! ",
      "type": "message",
      "timestamp": "2024-07-25T14:12:31.965Z"
    }
  ]
}
```
### POST

| url                                                       | Django tag                                     | Sign In required |
|-----------------------------------------------------------| ---------------------------------------------- | ---------------- |
| [chat/api/{chat_id}/messages/send/](#post-message)        | `{% url 'post-message' id %}`                  | ✅                |
| [chat/api/{chat_id}/leave/](#leave-chat)                  | `{% url 'leave-chat' id %}`                    | ✅                |
| [chat/api/{chat_id}/delete/](#delete-chat)                | `{% url 'delete-chat' id %}`                   | ✅                |
| [chat/api/{chat_id}/block/{player_id}](#block-player)     | `{% url 'block-player' chat_id player_id %}`   | ✅                |
| [chat/api/{chat_id}/unblock/{player_id}](#unblock-player) | `{% url 'unblock-player' chat_id player_id %}` | ✅                |
| [chat/api/{chat_id}/invite/{player_id}](#invite-player)   | `{% url 'invite-player' chat_id player_id %}`  | ✅                |
| [chat/api/{chat_id}/remove/{player_id}](#remove-player)   | `{% url 'remove-player' chat_id player_id %}`  | ✅                |

All actions return JSON response alike:
```json
{"message": "..."}
```
is action was successful, or
```json
{"error": "..."}
```
otherwise.
#### post-message
Action to post a message in specified chat. Message contents are sent as request body. Responses returned:
- *201*: Message posted successfully
- *400*: Message has empty body
- *403*: Player blocked you or is blocked by you 
- *404*: Chat with specified id not found
- *405*: Method is not **POST**
#### leave-chat
- *200*: Logged-in player was not in this chat
- *201*: Left chat successfully
- *400*: Logged-in player is a chat's **admin** or chat is a Dialogue
- *404*: Chat with specified id not found
- *405*: Method is not **POST**
#### delete-chat
- *201*: Chat deleted successfully
- *403*: Logged-in player is not in this chat and/or isn't admin
- *404*: Chat with specified id not found
- *405*: Method is not **POST**
#### block-player
This function blocks player on the **chat** level - adds player to *GroupChat* blockist, or to *Player*'s blocklist if *chat_id* points to the existing dialogue.
While `'players-action:block-player' id` from [player's actions](#get-available-actions) - on the **player** level just adds *player* by it's **id** to the logged-in player's blocklist.
- *200*: Player is already blocked
- *201*: Blocked successfully
- *403*: Logged-in player is not in this chat and/or isn't admin
- *404*: Chat and/or Player with specified id not found
- *405*: Method is not **POST**
#### unblock-player
Same as above: blocks player in GroupChat or in Dialogue, if Dialogue exists
- *200*: Player is not present in blocklist
- *201*: Unblocked successfully
- *403*: Logged-in player is not in this chat and/or isn't admin
- *404*: Chat and/or Player with specified id not found
- *405*: Method is not **POST**
#### invite-player
Invites player to the group chat.
- *200*: Player is already in the chat
- *201*: Player added successfully
- *403*: Logged-in player is not in this chat and/or isn't admin or Chat is a Dialogue - which can only have 2 players, no more - no less
- *404*: Chat and/or Player with specified id not found
- *405*: Method is not **POST**
#### remove-player
Removes player from the group chat.
- *200*: Player is already not in the chat
- *201*: Player removed successfully
- *403*: Logged-in player is not in this chat and/or isn't admin or Chat is a Dialogue - which can only have 2 players, no more - no less
- *404*: Chat and/or Player with specified id not found
- *405*: Method is not **POST**
### ws/chat/
By opening of the web socket on this address - django creates consumer that checks all messages in all chats in which logged-in player participates. All messages present at that moment are treated as "seen". Then, while client stays connected - django runs infinite cycle to track changes in the amount of messages in player's chats.
#### Django -> client
Whenever new messages appear in any of player's chats - message like this get's sent to the client:
```json
{
  "type": "unred_messages",
  "chat_id": 12,
  "amount_unseen": 1,
  "amount_total": 33
}
```
#### client -> Django
In order to mark "unread"  messages as "read" consumer expects message of the following format:
```json
{
  "type": "messages_checked",
  "chat_id": 12,
  "seen_messages": 33
}
```
