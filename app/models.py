from django.db import models
import uuid

class Type(models.Model):
    name = models.CharField(max_length=100, unique=True)  # タイプ名は一意
    def __str__(self):
        return self.name
    
class Pokemon(models.Model):
    name = models.CharField(max_length=100, unique=True)  # ポケモン名は一意
    types = models.ManyToManyField(Type, related_name="pokemons")

    def __str__(self):
        return self.name

class Player(models.Model):
    name = models.CharField(max_length=100)  # プレイヤー名は一意でなくてもOK
    pokemons = models.ManyToManyField(Pokemon, related_name="players")  # 多対多関係
    user_id = models.IntegerField(default=1)
    def __str__(self):
        return self.name


