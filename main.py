import asyncio
import datetime
import re
import os

from telebot.async_telebot import AsyncTeleBot, types
from tinydb import Query, TinyDB

from Openweather import OWM
from Settings import Settings
from Language import Language

#check folder db
if not os.path.exists('db'):
    os.makedirs('db')

users_db = TinyDB('db/users.json')
channel_db = TinyDB('db/channel.json')
setting = Settings()
language = Language()

bot = AsyncTeleBot(setting.TELEGRAM_BOT_TOKEN, parse_mode=None)
owm = OWM(setting.WEATHER_API_KEY, setting.WEATHER_EXCLUDE,
          setting.WEATHER_UNITS, setting.WEATHER_LANG)

clients = dict()


@bot.message_handler(commands=['start'])
async def start_message(message):
    # add chat_id to user
    clients[message.chat.id] = {'action': 0, 'type': 0}
    if not users_db.search(Query().chat_id == message.chat.id):
        users_db.insert({'chat_id': message.chat.id, 'city': '', 'country': '',
                         'auto_notify': False, 'auto_notify_time': '00:00', 'auto_notify_timezone': '+03:00'})
    await bot.send_message(message.chat.id, language.WELCOME_MESSAGE)


@bot.message_handler(commands=['about'])
async def about_message(message):
    await bot.send_message(message.chat.id, language.ABOUT_MESSAGE)


@bot.message_handler(commands=['weather'])
async def message(message):
    city = users_db.search(Query().chat_id == message.chat.id)[0]['city']
    country = users_db.search(Query().chat_id == message.chat.id)[0]['country']
    if city == '' or country == '':
        clients[message.chat.id]['action'] = 1
        markup = setting_keyboard(message.chat.id, 'cancel')
        await bot.send_message(message.chat.id, language.SET_CITY, reply_markup=markup)
        return
    await bot.send_message(message.chat.id, owm.build_data(city, country, 1))


@bot.message_handler(commands=['settings'])
async def settings_message(message):
    # Send a message and wait for a response
    clients[message.chat.id] = {'action': 0, 'type': 0}
    markup = setting_keyboard(message.chat.id, 'main')
    await bot.send_message(message.chat.id, language.SETTING, reply_markup=markup)


@bot.message_handler(commands=['help'])
async def help_message(message):
    clients[message.chat.id] = {'action': 0, 'type': 0}
    await bot.send_message(message.chat.id, language.HELP_MESSAGE)


@bot.message_handler(regexp='установить город')
async def set_city(message):
    clients[message.chat.id]['action'] = 1
    markup = setting_keyboard(message.chat.id, 'cancel')
    await bot.send_message(message.chat.id, language.SET_CITY, reply_markup=markup)


@bot.message_handler(regexp='настроить время автосводки')
async def set_auto_notify_time(message):
    clients[message.chat.id]['action'] = 2
    markup = setting_keyboard(message.chat.id, 'cancel')
    await bot.send_message(message.chat.id, language.SET_AUTO_NOTIFY_TIME, reply_markup=markup)


@bot.message_handler(regexp='настроить часовой пояс')
async def set_timezone(message):
    clients[message.chat.id]['action'] = 3
    markup = setting_keyboard(message.chat.id, 'cancel')
    await bot.send_message(message.chat.id, language.SET_TIMEZONE, reply_markup=markup)


@bot.message_handler(regexp='настроить бота в канале')
async def settup_channel(message):
    markup = setting_keyboard(message.chat.id, 'channel')
    await bot.send_message(message.chat.id, language.SETUP_CHANNEL, reply_markup=markup)


@bot.message_handler(regexp='добавить канал')
async def add_channel(message):
    # Add group
    clients[message.chat.id]['action'] = 4
    markup = setting_keyboard(message.chat.id, 'cancel')
    await bot.send_message(message.chat.id, language.ADD_CHANNEL, reply_markup=markup)


@bot.message_handler(regexp='мои каналы')
async def my_channel(message):
    clients[message.chat.id] = {'action': 5, 'type': 1}
    markup = setting_keyboard(message.chat.id, 'my_channel')
    await bot.send_message(message.chat.id, language.MY_CHANNEL, reply_markup=markup)

@bot.message_handler(regexp='отправить тестовое сообщение')
async def send_test_message(message):
    channel = channel_db.get(Query().channel_id == clients[message.chat.id]['channel_id'])
    clients[message.chat.id]['action'] = 0
    await bot.send_message(channel['channel_id'], owm.build_weather_data(channel['city'], channel['country'], 1))
    markup = setting_keyboard(message.chat.id, 'setup_channel')
    await bot.send_message(message.chat.id, language.SEND_TEST_MESSAGE, reply_markup=markup)


@bot.message_handler(regexp='включить автосводку')
async def enable_auto_notify(message):
    users_db.update({'auto_notify': True}, Query().chat_id == message.chat.id)
    markup = setting_keyboard(message.chat.id, 'setup_auto_notify')
    await bot.send_message(message.chat.id, language.AUTO_NOTIFY_ON, reply_markup=markup)


@bot.message_handler(regexp='отключить автосводку')
async def disable_auto_notify(message):
    users_db.update({'auto_notify': False}, Query().chat_id == message.chat.id)
    markup = setting_keyboard(message.chat.id, 'setup_auto_notify')
    await bot.send_message(message.chat.id, language.AUTO_NOTIFY_OFF, reply_markup=markup)


@bot.message_handler(regexp='Настроить автосводку')
async def set_auto_notify(message):
    markup = setting_keyboard(message.chat.id, 'setup_auto_notify')
    await bot.send_message(message.chat.id, language.SETTING, reply_markup=markup)


@bot.message_handler(regexp='отмена')
async def cancel_message(message):
    clients[message.chat.id] = {'action': 0, 'type': 0}
    await bot.send_message(message.chat.id, language.SET_CANCEL, reply_markup=types.ReplyKeyboardRemove())


@bot.message_handler(func=lambda message: True)
async def echo_all(message):
    if clients[message.chat.id]['action'] == 1:
        # Set city and country
        data = message.text.replace(' ', '')
        data = data.split(',')

        if clients[message.chat.id]['type'] == 0:
            users_db.update({'city': data[0], 'country': data[1]},
                            Query().chat_id == message.chat.id)
            clients[message.chat.id]['action'] = 0
            markup = setting_keyboard(message.chat.id, 'main')
            await bot.send_message(message.chat.id, language.SET_CITY_OK, reply_markup=markup)
        else:
            channel_db.update({'city': data[0], 'country': data[1]},
                              Query().channel_id == clients[message.chat.id]['channel_id'])
            clients[message.chat.id]['action'] = 0
            markup = setting_keyboard(message.chat.id, 'setup_channel')
            await bot.send_message(message.chat.id, language.SET_CITY_OK, reply_markup=markup)
    elif clients[message.chat.id]['action'] == 2:
        # Set time
        if clients[message.chat.id]['type'] == 0:
            if validate_time(message.text, 'time'):
                users_db.update({'auto_notify_time': message.text},
                                Query().chat_id == message.chat.id)
                clients[message.chat.id]['action'] = 0
                markup = setting_keyboard(message.chat.id, 'setup_auto_notify')
                await bot.send_message(message.chat.id, language.SET_AUTO_NOTIFY_TIME_OK, reply_markup=markup)
            else:
                await bot.send_message(message.chat.id, language.SET_AUTO_NOTIFY_TIME_ERROR)
        else:
            if validate_time(message.text, 'time'):
                channel_db.update({'auto_notify_time': message.text},
                                  Query().channel_id == clients[message.chat.id]['channel_id'])
                clients[message.chat.id]['action'] = 0
                markup = setting_keyboard(message.chat.id, 'setup_channel')
                await bot.send_message(message.chat.id, language.SET_AUTO_NOTIFY_TIME_OK, reply_markup=markup)
            else:
                await bot.send_message(message.chat.id, language.SET_AUTO_NOTIFY_TIME_ERROR)
    elif clients[message.chat.id]['action'] == 3:
        # Set timezone
        if clients[message.chat.id]['type'] == 0:
            if validate_time(message.text, 'timezone'):
                users_db.update({'auto_notify_timezone': message.text},
                                Query().chat_id == message.chat.id)
                clients[message.chat.id]['action'] = 0
                markup = setting_keyboard(message.chat.id, 'setup_auto_notify')
                await bot.send_message(message.chat.id, language.SET_TIMEZONE_OK, reply_markup=markup)
            else:
                await bot.send_message(message.chat.id, language.SET_TIMEZONE_ERROR)
        else:
            if validate_time(message.text, 'timezone'):
                channel_db.update({'auto_notify_timezone': message.text},
                                  Query().channel_id == clients[message.chat.id]['channel_id'])
                clients[message.chat.id]['action'] = 0
                markup = setting_keyboard(message.chat.id, 'setup_channel')
                await bot.send_message(message.chat.id, language.SET_TIMEZONE_OK, reply_markup=markup)
            else:
                await bot.send_message(message.chat.id, language.SET_TIMEZONE_ERROR)
    elif clients[message.chat.id]['action'] == 4:
        # Add group
        if validate_group(message):
            users_db.update({'groups': True},
                            Query().chat_id == message.chat.id)
            clients[message.chat.id]['action'] = 0
            await bot.send_message(message.chat.id, language.ADD_CHANNEL_OK, reply_markup=types.ReplyKeyboardRemove())
        else:
            await bot.send_message(message.chat.id, language.ADD_CHANNEL_ERROR)
    elif clients[message.chat.id]['action'] == 5:
        # get channel id by name
        clients[message.chat.id]['channel_id'] = channel_db.search(
            (Query().name == message.text) & (Query().admin == message.chat.id))[0]['channel_id']
        clients[message.chat.id]['type'] = 1
        markup = setting_keyboard(message.chat.id, 'setup_channel')
        await bot.send_message(message.chat.id, language.SETUP_CHANNEL, reply_markup=markup)


def validate_group(message):
    data = message.forward_from_chat
    if data.type == 'channel':
        # add group to channel
        if not channel_db.search(Query().channel_id == message.chat.id):
            channel_db.insert(
                {'channel_id': data.id, 'name': data.title, 'admin': message.chat.id, 'city': '', 'country': '', 'auto_notify': True, 'auto_notify_time': '00:00', 'auto_notify_timezone': '+03:00'})
        return True
    else:
        return False


def setting_keyboard(chat_id, kit):
    if kit == 'main':
        markup = types.ReplyKeyboardMarkup(
            one_time_keyboard=True, resize_keyboard=True)
        markup.row('Установить город')
        markup.row('Настроить бота в канале')
        markup.row('Настроить автосводку')
    elif kit == 'channel':
        markup = types.ReplyKeyboardMarkup(
            one_time_keyboard=True, resize_keyboard=True)
        markup.row('Добавить канал')
        markup.row('Мои каналы')
        markup.row('Отмена')
    elif kit == 'my_channel':
        markup = types.ReplyKeyboardMarkup(
            one_time_keyboard=True, resize_keyboard=True)
        for channel_user in channel_db.search(Query().admin == chat_id):
            markup.row(channel_user['name'])
        markup.row('Отмена')
    elif kit == 'setup_channel':
        markup = types.ReplyKeyboardMarkup(
            one_time_keyboard=True, resize_keyboard=True)
        markup.row('Установить город')
        markup.row('Настроить время автосводки')
        markup.row('Настроить часовой пояс')
        markup.row('Отправить тестовое сообщение')
        markup.row('Отмена')
    elif kit == 'setup_auto_notify':
        markup = types.ReplyKeyboardMarkup(
            one_time_keyboard=True, resize_keyboard=True)
        if users_db.search(Query().chat_id == chat_id)[0]['auto_notify']:
            markup.row('Отключить автосводку')
        else:
            markup.row('Включить автосводку')
        markup.row('Настроить время автосводки')
        markup.row('Настроить часовой пояс')
        markup.row('Отмена')
    elif kit == 'cancel':
        markup = types.ReplyKeyboardMarkup(
            one_time_keyboard=True, resize_keyboard=True)
        markup.row('Отмена')

    return markup


def validate_time(time, type):
    if type == 'time':
        regex = r"^([01][0-9]|2[0-3]):([0-5][0-9])$"
        return re.match(regex, time)
    elif type == 'timezone':
        regex = r"^([+-][0-9]{2}):([0-9]{2})$"
        return re.match(regex, time)


async def send_notification():
    """
    If the current time is equal to the user's time, send a notification
    """
    # Get all users
    while True:
        for user in users_db.search(Query().auto_notify == True):
            user_time_zone = user['auto_notify_timezone']
            user_time = user['auto_notify_time']
            time_zone_offset = datetime.timedelta(hours=int(
                user_time_zone.split(':')[0]), minutes=int(user_time_zone.split(':')[1]))
            curent_time = datetime.datetime.utcnow() + time_zone_offset
            curent_time = curent_time.strftime('%H:%M')
            if curent_time == user_time:
                await bot.send_message(user['chat_id'], owm.build_weather_data(user['city'], user['country'], 1))
        for channel in channel_db.search(Query().auto_notify == True):
            channel_time_zone = channel['auto_notify_timezone']
            channel_time = channel['auto_notify_time']
            time_zone_offset = datetime.timedelta(hours=int(channel_time_zone.split(':')[
                                                  0]), minutes=int(channel_time_zone.split(':')[1]))
            curent_time = datetime.datetime.utcnow() + time_zone_offset
            curent_time = curent_time.strftime('%H:%M')
            if curent_time == channel_time:
                await bot.send_message(channel['channel_id'], owm.build_weather_data(channel['city'], channel['country'], 1))

        await asyncio.sleep(60)


async def main():
    task1 = asyncio.create_task(
        bot.polling(timeout=10, non_stop=True))

    task2 = asyncio.create_task(
        send_notification())

    await task1
    await task2

if __name__ == "__main__":
    asyncio.run(main())
