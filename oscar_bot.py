import telebot
from telebot import types
import sqlite3 as sql
bot = telebot.TeleBot("1792611963:AAHpykGbmPG2S1SXpRbNRMqduBjwVU1-wiw")
red = telebot.TeleBot("1757379210:AAHPW73fQXFRKGgS94SCqsrYarVECv8vu0M")
keyboard1 = telebot.types.ReplyKeyboardMarkup()
keyboard1.row("Н1", "Н2", "Н3", "Н4", "Н5", "Н6", "Н7", "Н8", "Н9", "Н10")
names = {"сагдиана": "s",
         "сафира": "s",
         "юлдуз": "s",
         "марьям": "s",
         "мустафо": "s",
         "зафар": "s",
         "искандер": "s",
         "артур": "s",
         "жаъфар": "s",
         "холид": "s",
         "абдугани": "s",
         "абдурашид": "s",
         "даниель": "s",
         "саидхон": "s",
         "амирхон": "s",
         "хаёт": "s",
         "казимжон": "s",
         "стас": "s",
         "саидакбар": "s",
         "эрнст": "s"}
name = ""


@bot.message_handler(commands=["start"])
def start_message(message):
    markup = types.ReplyKeyboardRemove(selective=False)
    bot.send_message(message.chat.id, 'Здравствуйте, это бот голосования ежегодной премии "Едель". Для того чтобы продолжить отправьте своё имя.', reply_markup=markup)
    register(message)


@bot.message_handler(commands=["do_test"])
def do_test(message):
    con = sql.connect("noms.db")
    with con:
        cur = con.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS `noms` (`id` Integer, `nomination` STRING, `nominates` STRING)")
        cur.execute("SELECT nomination FROM `noms`")
        rows = cur.fetchall()
        keyboard = types.InlineKeyboardMarkup()
        z = 0
        for i in rows:
            i = i[0]
            nominate = types.InlineKeyboardButton(text=i, callback_data=f"N{z}")
            keyboard.row(nominate)
            z += 1
        bot.send_message(message.chat.id, "А теперь проголосуйте в каждой номинации", reply_markup=keyboard)
        cur.close()
        con.commit()


@bot.message_handler(content_types=["text"])
def send_text(message):
    if message.text == "Регистрация":
        start_message(message)
    elif message.text == "Голосование🗳":
        do_test(message)
    elif message.text == "Личный кабинет🔑":
        keyboard = telebot.types.ReplyKeyboardMarkup()
        keyboard.row("Ваши номинации", "Ваши данные")
        bot.send_message(message.chat.id, "Личный кабинет", reply_markup=keyboard)
    elif message.text == "Ваши данные":
        con = sql.connect("test.db")
        with con:
            cur = con.cursor()
            cur.execute("CREATE TABLE IF NOT EXISTS `test` (`name` STRING, `username` STRING, 'chat.id' Integer)")
            cur.execute(f"SELECT name FROM `test` WHERE chat.id = {message.chat.id}")
            a = cur.fetchall()
            cur.close()
            con.commit()


def register(message):
    bot.send_message(message.chat.id, "Ваше имя (без фамилии)")
    bot.register_next_step_handler(message, reg_name)


def reg_name(message):
    global name
    name = message.text.lower()
    if name in names:
        bot.send_message(message.chat.id, "Введите имя вашего любимого учителя")
        bot.register_next_step_handler(message, check)
    elif name not in names:
        bot.send_message(message.chat.id, "Введите ваше имя повторно. Его нет в базе данных.")
        register(message)


def check(message):
    d = names[name]
    if d == message.text:
        con = sql.connect("test.db")
        with con:
            cur = con.cursor()
            cur.execute("CREATE TABLE IF NOT EXISTS `test` (`name` STRING, `username` STRING, 'chat.id' Integer)")
            cur.execute(f"INSERT INTO `test` VALUES ('{name}', '{message.from_user.username}', '{message.chat.id}')")
            cur.close()
            con.commit()
        keyboard = telebot.types.ReplyKeyboardMarkup()
        keyboard.row("Голосование🗳")
        keyboard.row("Личный кабинет🔑")
        bot.send_message(message.chat.id, "Ура получилось!", reply_markup=keyboard)
    else:
        bot.send_message(message.chat.id, "Похоже вы ошиблись. Начните регистрацию заново")

        register(message)


@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    print(call.data)
    if "NO" not in call.data:
        con = sql.connect("noms.db")
        with con:
            cur = con.cursor()
            cur.execute("CREATE TABLE IF NOT EXISTS `noms` (`id` Integer, `nomination` STRING, `nominates` STRING)")
            cur.execute("SELECT nomination FROM `noms`")
            rows = cur.fetchall()
            z = len(rows)
            cur.close()
            con.commit()
        for i in range(z):
            if call.data == f"N{i}":
                con = sql.connect("noms.db")
                with con:
                    cur = con.cursor()
                    cur.execute(f"SELECT nominates FROM `noms` WHERE id={i}")
                    rows = cur.fetchall()
                    keyboard = types.InlineKeyboardMarkup()
                    rows = rows[0][0].split(",")
                    x = 0
                    for y in rows:
                        nominate = types.InlineKeyboardButton(text=y, callback_data=f"N{i}NO{x}")
                        keyboard.row(nominate)
                        x += 1
                    bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.id,
                                                  reply_markup=keyboard)
                    cur.close()
                    con.commit()
                break
    elif "NO" in call.data:
        con = sql.connect("noms.db")
        with con:
            cur = con.cursor()
            cur.execute("CREATE TABLE IF NOT EXISTS `noms` (`id` Integer, `nomination` STRING, `nominates` STRING)")
            cur.execute(f"SELECT nomination FROM `noms`")
            rows = cur.fetchall()
            cur.execute(f"SELECT nominates FROM `noms` WHERE id = {call.data[1]}")
            rows2 = cur.fetchall()
            rows2 = rows2[0][0].split(",")
            z = len(rows)
            x = len(rows2)
            cur.close()
            con.commit()
        for i in range(z):
            for y in range(x):
                print(f"N{i}NO{y}")
                if call.data == f"N{i}NO{y}":
                    r = open("бд.txt", "r")
                    r = r.readlines()
                    print(f"Номинация №{i} Номинант{y}")
                    r[i] = r[i].split(",")
                    r[i][y] = str(int(r[i][y]) + 1)
                    r[i] = ",".join(r[i])
                    r = "".join(r)
                    w = open("бд.txt", "w")
                    w.write(r)
                    break


bot.polling(none_stop=True)
