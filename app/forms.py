from django import forms
from .models import Player, Pokemon

class PlayerForm(forms.ModelForm):
    class Meta:
        model = Player
        fields = ['name', 'pokemons']  # nameとpokemonsをフォームに含める
        widgets = {
            'pokemons': forms.CheckboxSelectMultiple(),  # 複数選択用のチェックボックス
        } 
