import telebot

bot = telebot.TeleBot("7280096171:AAEFgQNfAv-bup-vVXUNKC7SOdk2oWJeWBo")
context, participants = {}, set()

@bot.message_handler(commands=["start"])
def welcome(message):
    bot.send_message(message.chat.id, "конференция началась") #приветствие
    bot.send_message(message.chat.id, "назовите игроков:")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    if message.from_user.id not in context:
        context[message.from_user.id] = message.text
        update_participants(message.chat.id) #обновление списка участников
        bot.reply_to(message, f"получил: {message.text}")

def update_participants(chat_id):
    global participants
    participants.clear()  # Очищаем предыдущее множество участников
    for member in bot.get_chat_administrators(chat_id):  # Получаем администраторов
        participants.add(member.user.username)  # Добавляем администраторов в список
    for member in bot.get_chat_members_count(chat_id):  # Получаем всех участников
        participants.add(member.user.username)  # Добавляем участников в список
    print("Участники:", participants)  # Выводим список участников
    print(*context)

if __name__ == "__main__": bot.polling(none_stop=True, interval=0)