from django.urls import path
from . import views


app_name = "app"
urlpatterns = [
    path("",views.index, name="index"),
    path("register_player", views.register_player, name='register_player'),  # プレイヤー登録
    path('register_player2/', views.register_player2, name='register_player2'),  # プレイヤー登録
    path('random_pick/', views.random_pick, name='random_pick'),  # ランダムピック
    path("edit_player/", views.edit_player, name="edit_player"),
    path("get_player_pokemons/", views.get_player_pokemons, name="get_player_pokemons"),
    path("assign_user_id/", views.assign_user_id, name="assign_user_id"),
    path("get_player_data/<int:player_id>/", views.get_player_data, name="get_player_data"),
    
]