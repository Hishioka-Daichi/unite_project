from django.shortcuts import render, redirect
from django.views import View
from .forms import PlayerForm
from .models import Player, Pokemon,Type



class IndexView(View):
    def get(self, request):
        form = PlayerForm()
        players = Player.objects.all()  # 全プレイヤーを取得
        all_pokemons = Pokemon.objects.all()  # 全てのポケモン
        types = Type.objects.all()
        pokemon_by_type = {}
        for poke_type in Type.objects.all():
            pokemon_by_type[poke_type.name] = Pokemon.objects.filter(types=poke_type)
        
        return render(request,"app/index.html",{"form":form,"players":players, "all_pokemons": all_pokemons,"pokemon_by_type":pokemon_by_type,"all_types":types})
    

from django.http import JsonResponse
from django.views import View
from .models import Player
from .forms import PlayerForm

class RegisterPlayerView(View):
    def get(self, request):
        form = PlayerForm()
        return render(request, "app/register_player.html", {"form": form})

    def post(self, request):
        form = PlayerForm(request.POST)

        # リクエストから user_id を取得
        user_id = request.POST.get("user_id")
        if not user_id:
            return JsonResponse({"error": "user_id が送信されていません。"}, status=400)

        if form.is_valid():
            player = form.save(commit=False)
            player.user_id = user_id  # user_id を保存
            player.save()
            return JsonResponse({
                "player": {
                    "id": player.id,  # プレイヤーのID
                    "name": player.name  # プレイヤーの名前
                }
            })
        return JsonResponse({"error": "フォームの検証に失敗しました。"}, status=400)




index = IndexView.as_view()
register_player = RegisterPlayerView.as_view()



from django.shortcuts import get_object_or_404
from django.http import JsonResponse

# サーバー側での受け取り例
def edit_player(request):
    if request.method == 'POST':
        player_id = request.POST.get('player_id')
        pokemons = request.POST.get('pokemons').split(',')

        # プレイヤーを取得してポケモンリストを更新
        player = Player.objects.get(id=player_id)
        selected_pokemons = Pokemon.objects.filter(id__in=pokemons)

        # プレイヤーのポケモンリストを更新
        player.pokemons.set(selected_pokemons)

        player.save()

        return JsonResponse({
            'player': {
                'id': player.id,
                'name': player.name,
                'pokemons': [pokemon.id for pokemon in player.pokemons.all()]
            }
        })


from django.shortcuts import get_object_or_404

def get_player_pokemons(request):
    player_id = request.GET.get("player_id")
    player = get_object_or_404(Player, id=player_id)
    pokemons = list(player.pokemons.values_list("id", flat=True))  # プレイヤーのポケモンIDを取得
    return JsonResponse({"pokemons": pokemons})





from django.shortcuts import render, redirect
from django.http import JsonResponse
from .forms import PlayerForm
def register_player2(request):
    if request.method == "POST":
        form = PlayerForm(request.POST)
        user_id=request.POST.get("user_id")
        if form.is_valid():
            # フォームのデータを保存
            player = form.save(commit=False)
            player.user_id = user_id  # user_id を保存
            player.save()

            # ポケモンを関連付ける
            pokemons = form.cleaned_data.get('pokemons')  # 選ばれたポケモンのインスタンスリスト
            player.pokemons.set(pokemons)  # プレイヤーとポケモンの多対多関係を設定
            return JsonResponse({
                "player": {
                    "id": player.id,  # プレイヤーのID
                    "name": player.name  # プレイヤーの名前
                }
            })
        else:
            return JsonResponse({"errors": form.errors}, status=400)
    else:
        form = PlayerForm()
    return False



import random
from django.http import JsonResponse
from .models import Player, Pokemon
from collections import Counter
def random_pick(request):
    if request.method == "POST":
        # フォームから送信された選択されたプレイヤーのIDを取得
        selected_player_ids = request.POST.getlist('players[]')
        toggle = request.POST.get('toggle') == 'true'  # チェックボックスの状態を取得（True/False）

        # プレイヤーを選択
        players = Player.objects.filter(id__in=selected_player_ids)

        results = {}  # 結果格納用
        selected_pokemons = set()  # 選ばれたポケモンを重複しないように追跡

        # チェックボックスがチェックされていなかった場合
        if not toggle:
            for player in players:
                # プレイヤーのポケモンをランダムに選ぶ（重複しないように）
                available_pokemons = player.pokemons.all()
                if available_pokemons.exists():
                    # 重複しないポケモンを選ぶ
                    available_pokemons = [pokemon for pokemon in available_pokemons if pokemon not in selected_pokemons]
                    
                    if available_pokemons:
                        random_pokemon = random.choice(available_pokemons)
                        selected_pokemons.add(random_pokemon)  # 選ばれたポケモンをセットに追加
                        results[player.id] = f"{player.name}: {random_pokemon.name}"
                    else:
                        results[player.id] = f"{player.name}: 選択できるポケモンがありません"
            sorted_results = {player.name: results[player.id] for player in players if player.id in results}
        # チェックボックスがチェックされていた場合、サポートとタンク担当を選ぶ
        else:
            # サポート担当とタンク担当のポケモンをランダムに選出する関数
            def select_support_and_tank(players):
                support_candidates = []
                tank_candidates = []
                support_pokemon_type = "support"
                tank_pokemon_type = "defense"

                # サポート担当とタンク担当を選出
                for player in players:
                    support_pokemon_list = []  # サポートタイプのポケモンを格納
                    tank_pokemon_list = []  # タンクタイプのポケモンを格納

                    # プレイヤーのポケモンからサポートとタンクのタイプを持っているポケモンを探す
                    for pokemon in player.pokemons.all():
                        # サポートタイプのポケモンをリストに追加
                        if support_pokemon_type in [ptype.name for ptype in pokemon.types.all()]:
                            support_pokemon_list.append(pokemon)
                        # タンクタイプのポケモンをリストに追加
                        if tank_pokemon_type in [ptype.name for ptype in pokemon.types.all()]:
                            tank_pokemon_list.append(pokemon)
                    
                    # サポート担当とタンク担当候補に追加
                    if support_pokemon_list:
                        support_candidates.append((player, support_pokemon_list))
                    if tank_pokemon_list:
                        tank_candidates.append((player, tank_pokemon_list))

                # サポート担当とタンク担当をランダムに選ぶ
                if support_candidates and tank_candidates:
                    # サポートとタンク担当が異なるプレイヤーから選ばれるようにする
                    random.shuffle(support_candidates)
                    random.shuffle(tank_candidates)

                    for support_player, support_pokemon_list in support_candidates:
                        for tank_player, tank_pokemon_list in tank_candidates:
                            if support_player != tank_player:  # 同じプレイヤーがサポートとタンク担当にならない
                                # サポートとタンク担当のポケモンが重複しないように選ぶ
                                support_pokemon = random.choice(support_pokemon_list)
                                tank_pokemon = random.choice(tank_pokemon_list)
                                if support_pokemon != tank_pokemon:
                                    selected_pokemons.add(support_pokemon)
                                    selected_pokemons.add(tank_pokemon)
                                    return support_player, support_pokemon, tank_player, tank_pokemon

                # 失敗した場合はNoneを返す
                return None, None, None, None

            # サポート担当とタンク担当を選ぶ
            support_player, support_pokemon, tank_player, tank_pokemon = select_support_and_tank(players)

            if support_player and tank_player:
                # サポートとタンク担当が決まった場合
                results[support_player.id] = f"{support_player.name}: {support_pokemon.name}"
                results[tank_player.id] = f"{tank_player.name}: {tank_pokemon.name}"

                MAX_RETRIES = 10

                for attempt in range(MAX_RETRIES):
                    # 残りのプレイヤーのみに対して結果を再構築
                    temp_results = {}
                    temp_selected_pokemons = selected_pokemons.copy()  # 既存の選択済みポケモンをコピー

                    # 残りのプレイヤーへのポケモン選定
                    remaining_players = [player for player in players if player.id not in results.keys()]
                    for player in remaining_players:
                        available_pokemons = player.pokemons.all()
                        # attack, balance, speedのタイプを持つポケモンを選ぶ
                        valid_pokemons = [pokemon for pokemon in available_pokemons if any(
                            ptype.name in ["attack", "balance", "speed"] for ptype in pokemon.types.all())]

                        # 重複しないポケモンを選ぶ
                        valid_pokemons = [pokemon for pokemon in valid_pokemons if pokemon not in temp_selected_pokemons]
                        
                        if valid_pokemons:
                            random_pokemon = random.choice(valid_pokemons)
                            temp_selected_pokemons.add(random_pokemon)
                            temp_results[player.id] = f"{player.name}: {random_pokemon.name}"
                        else:
                            temp_results[player.id] = f"{player.name}: マッチするポケモンが見つかりませんでした。"

                    # 全ての結果を一時的に統合
                    combined_results = {**results, **temp_results}
                    combined_selected_pokemons = temp_selected_pokemons

                    # 選ばれたポケモンのタイプを集計
                    all_selected_types = []
                    for pokemon in combined_selected_pokemons:
                        all_selected_types.extend([ptype.name for ptype in pokemon.types.all()])
                    
                    type_counts = Counter(all_selected_types)
                    # 同じタイプが3匹以上の場合、やり直し
                    if all(count < 3 for count in type_counts.values()):
                        # 結果を確定
                        results = combined_results
                        selected_pokemons = combined_selected_pokemons
                        break  # 条件を満たしている場合ループを抜ける
                else:
                    # 最大リトライ回数に達した場合
                                    results = {"error": "サポート担当またはタンク担当の選出に失敗しました。"}
                sorted_results = results
            else:
                results = {"error": "サポート担当またはタンク担当の選出に失敗しました。"}
                sorted_results = results
        # 結果をプレイヤーID順にソートして返す
        

        return JsonResponse({"results": sorted_results})

    return JsonResponse({"error": "Invalid request method"}, status=400)



import random
from django.http import JsonResponse

class AssignUserIdView(View):
    def get(self, request):
        # 一意の user_id を生成 (1～1000 の範囲)
        existing_user_ids = set(Player.objects.values_list('user_id', flat=True))  # 既存の user_id を取得
        available_ids = set(range(1, 1001)) - existing_user_ids  # 利用可能な ID を計算
        
        if not available_ids:
            return JsonResponse({"error": "すべてのIDが使用されています。"}, status=400)

        new_user_id = random.choice(list(available_ids))  # 利用可能な ID からランダムに選ぶ
        return JsonResponse({"user_id": new_user_id})

assign_user_id = AssignUserIdView.as_view()



from django.http import JsonResponse
from django.shortcuts import get_object_or_404

def get_player_data(request, player_id):
    player = get_object_or_404(Player, id=player_id)
    name=player.name
    pokemons = list(player.pokemons.values_list("id", flat=True))
    return JsonResponse({"pokemons": pokemons,"name":name})
