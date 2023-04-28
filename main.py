from aiogram import Bot, Dispatcher, executor, types, filters
from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton
from game import Matchmaking, Storage

bot_token = "Your_token"

bot = Bot(token=bot_token)
dp = Dispatcher(bot)

#from Dictionary to string
translator = {
    0: '⬜',
    1: '⭕',
    2: '❌',
    'cross': '❌',
    'zero': '⭕'
}

ctx = Storage()
MatchmakingHelper = Matchmaking()


#That where we use translator dict
def toStr(game_field):
    final_string = ""
    for id in game_field:
        for i in game_field[id]:
            final_string += "{} ".format(translator[i])
        final_string += "\n"
    return final_string


#Keyboards
button_start = InlineKeyboardButton('🔥 Начать поиск игры! 🔥', callback_data='start_matchmaking')
start_kb = InlineKeyboardMarkup()
start_kb.add(button_start)

button_stop = InlineKeyboardButton('⬅ Остановить поиск игры ⬅', callback_data='stop_matchmaking')
stop_kb = InlineKeyboardMarkup()
stop_kb.add(button_stop)

button_stop = InlineKeyboardButton('Сдаться', callback_data='give_up')
give_up = InlineKeyboardMarkup()
give_up.add(button_stop)

def generate_keyboard(game_field):
    game_kb = InlineKeyboardMarkup()
    for i in ['A', 'B', 'C']:
        button_1 = InlineKeyboardButton('{}'.format(translator[game_field[i][0]]), callback_data='hod {} 0'.format(i))
        button_2 = InlineKeyboardButton('{}'.format(translator[game_field[i][1]]), callback_data='hod {} 1'.format(i))
        button_3 = InlineKeyboardButton('{}'.format(translator[game_field[i][2]]), callback_data='hod {} 2'.format(i))
        game_kb.row(button_1, button_2, button_3)
    button_10 = InlineKeyboardButton('Сдаться', callback_data='give_up')
    game_kb.row(button_10)
    return game_kb

#And bot itself

@dp.message_handler(commands=['start'])
async def welcome(message: types.Message):
    if ctx.check_key(message['from']) != True:
        mes = await message.answer("Добро пожаловать в крестики нолики", reply_markup=start_kb)
        ctx.set_key(message['from'], mes)
    else:
        mes = ctx.get_key(message['from'])
        await mes.delete()
        mes = await message.answer("Добро пожаловать в крестики нолики", reply_markup=start_kb)
        ctx.set_key(message['from'], mes)

@dp.callback_query_handler(lambda c: c.data == "give_up")
async def instant_win(call: types.CallbackQuery):
    user = call['from']
    server_name = MatchmakingHelper.find_opponent(user)
    player = MatchmakingHelper.get_second_player(server_name, user)
    game_info = MatchmakingHelper.get_game_info(server_name)
    MatchmakingHelper.end_the_game(server_name)
    print("{} {} сдался, {} {} победил".format(user['first_name'], user['last_name'], player['first_name'], player['last_name']))
    mes_from_player = ctx.get_key(player)
    mes_from_user = ctx.get_key(user)

    # CHECK ON THE LAST NAME--------------------------

    if user['last_name'] == None:
        user['last_name'] = ""
    if player['last_name'] == None:
        player['last_name'] = ""

    # CHECK ON THE LAST NAME--------------------------

    await mes_from_player.edit_text("💚 Поздавляем, ваш противник {} {} сдался 💚 \n  \n{}".format(user['first_name'], user['last_name'], toStr(game_info['game_field'])))
    await mes_from_user.edit_text("🤡 К сожалению, вы сдались игроку {} {} 🤡 \n \n{}".format(player['first_name'], player['last_name'], toStr(game_info['game_field'])))
    new_mes_for_winner = await bot.send_message(player['id'], "Добро пожаловать в крестики нолики", reply_markup=start_kb)
    new_mes_for_loser = await bot.send_message(user['id'], "Добро пожаловать в крестики нолики", reply_markup=start_kb)
    ctx.set_key(player, new_mes_for_winner)
    ctx.set_key(user, new_mes_for_loser)

@dp.callback_query_handler(lambda c: c.data == "stop_matchmaking")
async def stop_search(callback_query: types.CallbackQuery):
    await callback_query.message.edit_text("Добро пожаловать в крестики нолики", reply_markup=start_kb)
    print("{} {} остановил поиск игры.".format(callback_query['from']['first_name'], callback_query['from']['last_name']))
    return MatchmakingHelper.delete_player_from_pool(callback_query['from'])

@dp.callback_query_handler(lambda c: c.data == "start_matchmaking")
async def start_search(callback_query: types.CallbackQuery):
    await callback_query.message.edit_text("Подбор противника начался, ожидайте.", reply_markup=stop_kb)
    user = callback_query['from']
    print("{} {} начал поиск игры.".format(user['first_name'], user['last_name']))
    status = await MatchmakingHelper.start_matchmaking(user)
    if status != 0:
        player = ctx.get_key(user)
        status1 = ctx.get_key(status[1])
        print("Начался матч: {} {} против {} {}".format(status[1]['first_name'], status[1]['last_name'], user['first_name'], user['last_name']))
        game_info = MatchmakingHelper.start_game(status[0])
        game_kb = generate_keyboard(game_info['game_field'])

        #CHECK ON THE LAST NAME--------------------------

        if user['last_name'] == None:
            user['last_name'] = ""
        if status[1]['last_name'] == None:
            status[1]['last_name'] = ""

        # CHECK ON THE LAST NAME--------------------------

        if game_info['current_player'] == user:
            await player.edit_text("Ваш противник {} {}. \n \nCейчас ваш ход, вы играете за {} ".format(status[1]['first_name'], status[1]['last_name'], translator[MatchmakingHelper.get_player_side(status[0], user)]), reply_markup=game_kb)
            await status1.edit_text("Ваш противник {} {}. \n \n{} \n Cейчас ход противника".format(user['first_name'], user['last_name'], toStr(game_info['game_field'])), reply_markup=give_up)
        else:
            await status1.edit_text("Ваш противник {} {}. \n \nCейчас ваш ход, вы играете за {} ".format(user['first_name'], user['last_name'], translator[MatchmakingHelper.get_player_side(status[0], status[1])]), reply_markup=game_kb)
            await player.edit_text("Ваш противник {} {}. \n \n{} \n Cейчас ход противника".format(status[1]['first_name'], status[1]['last_name'], toStr(game_info['game_field'])), reply_markup=give_up)

@dp.callback_query_handler(lambda c: c.data and c.data.startswith('hod'))
async def click(call: types.CallbackQuery):
    coords = call.data[4:]
    user = call['from']
    server_name = MatchmakingHelper.find_opponent(user)
    if server_name != None:
        game_info = MatchmakingHelper.get_game_info(server_name)
        current_player = game_info['current_player']
        if current_player == user:
            status = MatchmakingHelper.do_click(server_name, coords)
            if status == False:
                return await bot.answer_callback_query(call.id, text='Клетка уже занята', show_alert=True)
            elif status == True:
                game_info = MatchmakingHelper.get_game_info(server_name)
                game_kb = generate_keyboard(game_info['game_field'])
                mes_for_user = ctx.get_key(user)
                mes_for_player = ctx.get_key(game_info['current_player'])

                #CHECK ON THE LAST NAME--------------------------

                if user['last_name'] == None:
                    user['last_name'] = ""
                if game_info['current_player']['last_name'] == None:
                    game_info['current_player']['last_name'] = ""

                # CHECK ON THE LAST NAME--------------------------

                await mes_for_user.edit_text("Ваш противник {} {}. \n \n{} \n Cейчас ход противника".format(game_info['current_player']['first_name'], game_info['current_player']['last_name'], toStr(game_info['game_field'])), reply_markup=give_up)
                await mes_for_player.edit_text("Ваш противник {} {}. \n \nCейчас ваш ход, вы играете за {}".format(user['first_name'], user['last_name'], translator[MatchmakingHelper.get_player_side(server_name, game_info['current_player'])]), reply_markup=game_kb)
            else:
                mes_for_winner = ctx.get_key(status['winner'])
                mes_for_loser = ctx.get_key(status['loser'])

                #CHECK ON THE LAST NAME--------------------------

                if status['winner']['last_name'] == None:
                    status['winner']['last_name'] = ""
                if status['loser']['last_name'] == None:
                    status['loser']['last_name'] = ""

                # CHECK ON THE LAST NAME--------------------------

                if status['match_result'] == 'win':
                    print("Матч закончился: {} {} победил, {} {} проиграл".format(status['winner']['first_name'], status['winner']['last_name'], status['loser']['first_name'], status['loser']['last_name']))
                    await mes_for_winner.edit_text("💚 Поздавляем, вы выиграли игрока {} {} 💚 \n  \n{}".format(toStr(status['game_field']), status['loser']['first_name'], status['loser']['last_name']))
                    await mes_for_loser.edit_text("🤡 К сожалению, вы проиграли игроку {} {} 🤡 \n \n{}".format(toStr(status['game_field']), status['winner']['first_name'], status['winner']['last_name']))
                    new_mes_for_winner = await bot.send_message(status['winner']['id'], "Добро пожаловать в крестики нолики", reply_markup=start_kb)
                    new_mes_for_loser = await bot.send_message(status['loser']['id'], "Добро пожаловать в крестики нолики", reply_markup=start_kb)
                    ctx.set_key(status['winner'], new_mes_for_winner)
                    ctx.set_key(status['loser'], new_mes_for_loser)
                if status['match_result'] == 'draw':
                    print("Матч закончился: {} {} ничья с {} {} ".format(status['winner']['first_name'], status['winner']['last_name'], status['loser']['first_name'], status['loser']['last_name']))
                    await mes_for_winner.edit_text("👤 У вас ничья с {} {} 👤 \n \n {}".format(toStr(status['game_field']), status['loser']['first_name'], status['loser']['last_name']))
                    await mes_for_loser.edit_text("👤 У вас ничья с {} {} 👤 \n \n {}".format(toStr(status['game_field']), status['winner']['first_name'], status['winner']['last_name']))
                    new_mes_for_winner = await bot.send_message(status['winner']['id'], "Добро пожаловать в крестики нолики", reply_markup=start_kb)
                    new_mes_for_loser = await bot.send_message(status['loser']['id'], "Добро пожаловать в крестики нолики", reply_markup=start_kb)
                    ctx.set_key(status['winner'], new_mes_for_winner)
                    ctx.set_key(status['loser'], new_mes_for_loser)


#start our bot
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
