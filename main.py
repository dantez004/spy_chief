import threading#для остановки
import telebot#для работы бота
from random import *#для логики ботa

bot = telebot.TeleBot(open("token.env", 'r').readline().strip())
print('token: ', open("token.env", 'r').readline().strip()) #просто вывод токена
stop_flag = threading.Event()
register_players, registered_users, list_players = {}, set(), []


@bot.message_handler(commands=["help"])
def send_help(message):
    bot.send_message(message.chat.id, "Для регистрации всем игрокам необходимо использовать /start (бот сообщит о прохождении регистрации)\n\nДля запуска игры необходимо использовать /game\n\nЧтобы закончить игру и узнать кто был шпионом есть команда /whospy\n\nДля запуска опроса необходимо использовать /voting\n")

@bot.message_handler(commands=["start"])  # регистрация
def handle_start(message):
    chatid = message.chat.id
    usid = message.from_user.id
    usname = message.from_user.username

    if chatid not in register_players:  # регистрация пользователей
        register_players[chatid] = []

    if usid not in register_players[chatid]:  # проверка зарегистрирован ли пользователь
        register_players[chatid].append(usid)
        bot.send_message(chatid, f"записал @{usname}")
        list_players.append(usname) #учёт имени пользователя (может понадобиться для опроса
    else:
        bot.send_message(chatid, f"@{usname} уже записан")


    print(f"{register_players=},{registered_users=}")  # отлодка


    if len(register_players[chatid]) >= bot.get_chat_members_count(
            chatid) - 1:  # проверка регистрации всех пользователей чата
        #bot.send_message(chatid, "теперь жду /game")    #включает напоминалку как продолжить
        handle_game(message)
        registered_users.update(register_players[chatid])  # обновление множества зарег.пользователей


@bot.message_handler(commands=["game"])
def handle_game(message):   #начало игры
    chatid = message.chat.id

    if chatid not in register_players or not register_players[chatid]:      #проверка на существование игроков
        bot.send_message(chatid, "нет записанных игроков. Используйте /start для записи")
        return

    players = register_players[chatid]
    playernames = [bot.get_chat_member(chatid, uid).user.username for uid in players]   #получает имена игроков

    bot.send_message(chatid, "игра начинается") #объявляет начало игры
    bot.send_message(chatid, f"участники: {', '.join(playernames)}")    #пишет список участников
    logic_game(message) #запускает логику игры


def logic_game(message, flag_spy_opened=False):  # логика игры
    global spy
    word = choice([i.strip() for i in open("database.txt", 'r', encoding="utf-8-sig").readlines()]) #считывание базы слов
    players = register_players[message.chat.id]     #берёт список участников (записаны их id)

    if (flag_spy_opened):   #если шпион раскрыт, то добавляет его в список участников
        players.append(spy)
        return

    spy = choice(players)   #выбирает шпиона
    players.remove(spy) #удаляет шпиона из списка участников

    bot.send_message(spy, "ты шпион")   #отправляет шпиону сообещние
    for player in players:  #отправляет не-шпионам слово для игры
        bot.send_message(player, word)

@bot.message_handler(command=["voting"]) #голосование
def send_vote(message):
    bot.send_poll(message.chat.id, "Кто шпион?", options=register_players[message.chat.id]) #запуск опроса

@bot.message_handler(commands=["whospy"]) #вывод кто был шпионом
def whospy(message):
    global spy
    bot.send_message(message.chat.id, f"Шпионом был {bot.get_chat_member(message.chat.id, spy).user.username}") #вывод кто был шпионом
    logic_game(message, flag_spy_opened=True) #доабвление шпиона к остальным игрокам

@bot.message_handler(commands=["stop"])
def stop_bot(message):
    bot.send_message(message.chat.id, "ботяра говорит пока")
    stop_flag.set() #останоква бота

bot.polling(none_stop=True, interval=0)
