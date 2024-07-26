from django.urls import path
from . import views

urlpatterns = [
    path('', views.game, name='game'),
    path('solo/', views.solo, name='solo'),

    path('api/match/invite/<int:player_id>/', views.invite, name='invite'),
    path('api/match/check/<str:game_id>/', views.check, name='check'),
    path('api/match/accept/<str:game_id>/', views.accept, name='accept'),
    path('api/match/proceed/<str:game_id>/', views.proceed, name='proceed'),
    path('api/match/decline/<str:game_id>/', views.decline, name='decline'),

    path('api/tournament/create/', views.create_tournament, name='create_tournament'),
    path('api/tournament/subscribe/', views.subscribe_tournament, name='subscribe_tournament'),
    path('api/tournament/records/<int:record_id>/', views.get_tournament_info, name='tournament-info'),
    path('api/tournament/records/<int:record_id>/player/<int:player_id>', views.get_tournament_player_stat, name='tournament-player-stat'),

    path('api/records/get/<int:record_id>/', views.get_record_info, name='get-record-info'),
]
