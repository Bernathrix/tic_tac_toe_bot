import uuid
import random

#Tic Tac Toe main class
class Game:
    def __init__(self):
        self.pool = {
            'default': {
                'tg_id': 'finding or server_name',
            },
        }
        self.servers = {
            #tg_id: server_name
            'server_name': {
                'zero': 'tg_id',
                'cross': 'tg_id',
                'status': 'online or gg',
                'game_info': 'dict of current pool and etd',
            }
        }

    def delete_player_from_pool(self, user):
        self.pool['default'][user] = 0

    def get_player_side(self, server_name, user):
        if self.servers[server_name]['cross'] == user:
            return 'cross'
        else:
            return 'zero'

    def start_game(self, server_name):
        if server_name in self.servers:
            if self.servers[server_name]['status'] == 'starting':
                self.servers[server_name]['status'] = 'started'
                game_field = {
                    'A': [0, 0, 0],
                    'B': [0, 0, 0],
                    'C': [0, 0, 0],
                }
                current_player = self.servers[server_name]['zero']
                game_info = {
                    'game_field': game_field,
                    'current_player': current_player,
                }
                self.servers[server_name]['game_info'] = game_info
                return self.servers[server_name]['game_info']

    def get_game_info(self, server_name):
        if server_name in self.servers:
            return self.servers[server_name]['game_info']

    def get_second_player(self, server_name, user):
        if self.servers[server_name]['cross'] == user:
            return self.servers[server_name]['zero']
        else:
            return self.servers[server_name]['cross']

    def end_the_game(self, server_name):
        player1 = self.servers[server_name]['cross']
        player2 = self.servers[server_name]['zero']
        self.delete_player_from_pool(player1)
        self.delete_player_from_pool(player2)
        self.servers.pop(server_name)

    def do_click(self, server_name, coord):
        coord = coord.split(' ')
        coord[1] = int(coord[1])
        game_info = self.get_game_info(server_name)
        if game_info['game_field'][coord[0]][coord[1]] != 0:
            return False
        user = game_info['current_player']
        side = self.get_player_side(server_name, user)
        if side == "cross":
            game_info['game_field'][coord[0]][coord[1]] = 2
            game_info['current_player'] = self.servers[server_name]['zero']
        if side == "zero":
            game_info['game_field'][coord[0]][coord[1]] = 1
            game_info['current_player'] = self.servers[server_name]['cross']
        self.servers[server_name]['game_info'] = game_info
        status = self.check_on_the_end(game_info['game_field'], server_name)
        if status == None:
            return True
        else:
            self.end_the_game(server_name)
            return status


    def to_list(self, game_field):
        cross = []
        zero = []
        for i in range(3):
            if game_field['A'][i] == 1:
                zero.append("A {}".format(i))
            if game_field['A'][i] == 2:
                cross.append("A {}".format(i))
        for i in range(3):
            if game_field['B'][i] == 1:
                zero.append("B {}".format(i))
            if game_field['B'][i] == 2:
                cross.append("B {}".format(i))
        for i in range(3):
            if game_field['C'][i] == 1:
                zero.append("C {}".format(i))
            if game_field['C'][i] == 2:
                cross.append("C {}".format(i))
        return {
            'zero': zero,
            'cross': cross,
        }

    def check_on_the_end(self, game_field, server_name):
        res = self.to_list(game_field)
        cross = res['cross']
        zero = res['zero']
        draw = True
        for i in range(3):
            if game_field['A'][i] == 0:
                draw = False
        for i in range(3):
            if game_field['B'][i] == 0:
                draw = False
        for i in range(3):
            if game_field['C'][i] == 0:
                draw = False
        win_combinations = [['A 0', 'A 1', 'A 2'],
                            ['B 0', 'B 1', 'B 2'],
                            ['C 0', 'C 1', 'C 2'],
                            ['A 0', 'B 0', 'C 0'],
                            ['A 1', 'B 1', 'C 1'],
                            ['A 2', 'B 2', 'C 2'],
                            ['A 0', 'B 1', 'C 2'],
                            ['A 2', 'B 1', 'C 0'],
                            ]
        for i in win_combinations:
            if i[0] in cross:
                if i[1] in cross:
                    if i[2] in cross:
                        return {
                            "match_result": "win",
                            "winner": self.servers[server_name]['cross'],
                            "loser": self.servers[server_name]['zero'],
                            "game_field": game_field
                        }
            if i[0] in zero:
                if i[1] in zero:
                    if i[2] in zero:
                        return {
                            "match_result": "win",
                            "winner": self.servers[server_name]['zero'],
                            "loser": self.servers[server_name]['cross'],
                            "game_field": game_field
                        }
        if draw == True:
            return {
                "match_result": "draw",
                "winner": self.servers[server_name]['zero'],
                "loser": self.servers[server_name]['cross'],
                "game_field": game_field
            }
        return None

class Storage():
    def __init__(self):
        self.__key = {}

    def set_key(self, key, res):
        self.__key[key] = res

    def get_key(self, key):
        return self.__key[key]

    def check_key(self, key):
        if key in self.__key:
            return True
        else:
            return False

#Matchmaking additions
class Matchmaking(Game):
    def find_opponent(self, tg_id):
        if tg_id in self.pool['default']:
            if self.pool['default'][tg_id] != 'search':
                return self.pool['default'][tg_id]
        return None

    def get_server_name(self, user):
        return self.pool['default'][user]

    def find_available_player(self, user):
        for i in self.pool['default']:
            if self.pool['default'][i] == 'search':
                return i
        self.pool['default'][user] = 'search'
        return 0

    async def start_matchmaking(self, user):
        handler = self.find_available_player(user)
        if handler == 0:
            return 0
        else:
            if handler == user:
                await bot.send_message(handler, 'Вы уже начали поиск')
                return 0
            server_name = str(uuid.uuid4())
            self.pool['default'][handler] = server_name
            self.pool['default'][user] = server_name
            randint = random.randint(1, 2)
            if randint == 1:
                cross = user
                zero = handler
            else:
                cross = handler
                zero = user
            self.servers[str(server_name)] = {
                'zero': zero,
                'cross': cross,
                'status': 'starting',
                'game_info': 'idk',
            }
            return [str(server_name), handler]