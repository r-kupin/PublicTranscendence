from django.urls import include, path
from .views import auth_views, auth_intra_views, lobby_views, api_views, CustomPasswordChangeView

urlpatterns = [
    path('', auth_views.index, name='index'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('intra-callback/', auth_intra_views.intra_callback, name='intra-callback'),

    # ----------API Player retrieve data
    # Particular player
    path('api/players/', include(([
        path('me/', api_views.get_my_info, name='get-my-info'),
        path('<int:player_id>/', api_views.get_player_info, name='get-player-info'),
        path('me/<int:player_id>/', api_views.get_related_played_info, name='get-related-player-info'),
        path('<int:player_id>/actions/', api_views.get_available_actions, name='get-available-actions'),
    ], 'players'))),
    # All players
    path('api/players/all/', include(([
        path('', api_views.get_all_players, name='list'),
        path('except-me/', api_views.all_players_except_me, name='except-me'),
        path('online/', api_views.players_online, name='online'),
        path('online/except-me/', api_views.players_online_except_me, name='online-except-me'),
    ], 'all-players'))),
    # ----------API Player actions to perform
    path('api/players/<int:player_id>/', include(([
        path('add-friend/', api_views.add_to_friendlist, name='add-to-friendlist'),
        path('remove-friend/', api_views.remove_from_friendlist, name='remove-from-friendlist'),
        path('remove-dialogue/', api_views.remove_dialogue, name='remove-dialogue'),
        path('create-dialogue/', api_views.create_dialogue, name='create-dialogue'),
        path('unblock/', api_views.unblock_player, name='unblock-player'),
        path('block/', api_views.block_player, name='block-player'),
    ], 'players-action'))),

    path('bind-intra/', auth_intra_views.bind_intra, name='bind-intra'),
    path('sign-in-intra/', auth_intra_views.sign_in_intra, name='sign-in-intra'),
    path('sign-up-intra/', auth_intra_views.sign_up_intra, name='sign-up-intra'),
    path('set-image-from-intra/', auth_intra_views.set_image_from_intra, name='set-image-from-intra'),
    path('change-password/', CustomPasswordChangeView.as_view(), name='password_change'),

    path('signup/', auth_views.signup, name="signup"),

    path('home/', lobby_views.home, name='home'),
    path('profile/', lobby_views.profile, name="profile"),
    path('stats/', lobby_views.stats, name="stats"),
    path('settings/', lobby_views.settings, name="settings"),

]
