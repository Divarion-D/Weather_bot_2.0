import asyncio
import datetime
import re
import logging

from telebot.async_telebot import AsyncTeleBot, types
from tinydb import Query, TinyDB

from Openweather import OWM
from Settings import Settings

user = TinyDB('users.json')
channel = TinyDB('channel.json')
setting = Settings()

bot = AsyncTeleBot(setting.TELEGRAM_BOT_TOKEN, parse_mode=None)
owm = OWM(setting.WEATHER_API_KEY, setting.WEATHER_EXCLUDE,
          setting.WEATHER_UNITS, setting.WEATHER_LANG)

clients = dict()

@bot.message_handler(commands=['start'])
async def start_message(message):

    # add chat_id to user
    if not user.search(Query().chat_id == message.chat.id):
        user.insert({'chat_id': message.chat.id, 'city': '', 'country': '',
                     'auto_notify': False, 'auto_notify_time': '00:00', 'auto_notify_timezone': '+03:00', 'groups': False})

    await bot.send_message(message.chat.id, setting.WELCOME_MESSAGE)


@bot.message_handler(commands=['about'])
async def about_message(message):
    await bot.send_message(message.chat.id, setting.ABOUT_MESSAGE)


@bot.message_handler(commands=['weather'])
async def weather_message(message):
    city = user.search(Query().chat_id == message.chat.id)[0]['city']
    country = user.search(Query().chat_id == message.chat.id)[0]['country']
    if city == '' or country == '':
        clients[message.chat.id]['action'] = 1
        markup = setting_keyboard(message.chat.id, 'cancel')
        await bot.send_message(message.chat.id, setting.COMMAND_WEATHER_SET_CITY, reply_markup=markup)
        return
    await bot.send_message(message.chat.id, build_weather_data(city, country, 1))

# get chat_id from replay_message


@bot.message_handler(commands=['settings'])
async def settings_message(message):
    # Send a message and wait for a response
    markup = setting_keyboard(message.chat.id, 'main')
    await bot.send_message(message.chat.id, setting.COMMAND_SETTING, reply_markup=markup)


@bot.message_handler(func=lambda message: True)
async def echo_all(message):
    if message.text.lower() == 'установить город':
        # Set city and country
        clients[message.chat.id] = {'action': 1, 'type': 0}

        markup = types.ReplyKeyboardMarkup(
            one_time_keyboard=True, resize_keyboard=True)
        markup.row('Отмена')
        await bot.send_message(message.chat.id, setting.COMMAND_WEATHER_SET_CITY, reply_markup=markup)
    elif message.text.lower() == 'включить автоматическое уведомление':
        # Set auto notify
        user.update({'auto_notify': True}, Query().chat_id == message.chat.id)
        markup = setting_keyboard(message.chat.id, 'main')
        await bot.send_message(message.chat.id, setting.COMMAND_WEATHER_SET_AUTO_NOTIFY_ON, reply_markup=markup)
    elif message.text.lower() == 'отключить автоматическое уведомление':
        # Set auto notify
        user.update({'auto_notify': False}, Query().chat_id == message.chat.id)
        markup = setting_keyboard(message.chat.id, 'main')
        await bot.send_message(message.chat.id, setting.COMMAND_WEATHER_SET_AUTO_NOTIFY_OFF, reply_markup=markup)
    elif message.text.lower() == 'отмена':
        # Cancel
        clients[message.chat.id] = {'action': 0, 'type': 0}
        await bot.send_message(message.chat.id, setting.COMMAND_WEATHER_SET_CANCEL, reply_markup=types.ReplyKeyboardRemove())
    elif message.text.lower() == 'настроить автоматическое уведомление':
        # Setting auto notify
        clients[message.chat.id] = {'action': 2, 'type': 0}
        markup = types.ReplyKeyboardMarkup(
            one_time_keyboard=True, resize_keyboard=True)
        markup.row('Отмена')
        await bot.send_message(message.chat.id, setting.COMMAND_WEATHER_SET_AUTO_NOTIFY_TIME, reply_markup=markup)
    elif message.text.lower() == 'добавить группу':
        # Add group
        clients[message.chat.id] = {'action': 4, 'type': 0}
        markup = types.ReplyKeyboardMarkup(
            one_time_keyboard=True, resize_keyboard=True)
        markup.row('Отмена')
        await bot.send_message(message.chat.id, setting.COMMAND_WEATHER_SET_GROUP_ADD, reply_markup=markup)
    elif message.text.lower() == 'настроить бота в группе':
        # Setting bot in group
        clients[message.chat.id] = {'action': 5, 'type': 1}
        markup = types.ReplyKeyboardMarkup(
            one_time_keyboard=True, resize_keyboard=True)
        for channel_user in channel.search(Query().admin == message.chat.id):
            markup.row(channel_user['name'])
        markup.row('Отмена')
        await bot.send_message(message.chat.id, setting.COMMAND_SETTING, reply_markup=markup)
    elif clients[message.chat.id]['action'] == 1:
        # Set city and country
        data = message.text.split(',')
        if clients[message.chat.id]['type'] == 0:
            user.update({'city': data[0], 'country': data[1]},
                        Query().chat_id == message.chat.id)
            clients[message.chat.id]['action'] = 0
            await bot.send_message(message.chat.id, setting.COMMAND_WEATHER_SET_CITY_OK, reply_markup=types.ReplyKeyboardRemove())
        else:
            channel.update({'city': data[0], 'country': data[1]},
                           Query().channel_id == clients[message.chat.id]['channel_id'])
            clients[message.chat.id]['action'] = 2
            await bot.send_message(message.chat.id, setting.COMMAND_WEATHER_SET_AUTO_NOTIFY_TIME)        
    elif clients[message.chat.id]['action'] == 2:
        # Set time for auto notify
        if clients[message.chat.id]['type'] == 0:
            if validate_time(message.text, 'time'):
                user.update({'auto_notify_time': message.text},
                            Query().chat_id == message.chat.id)
                clients[message.chat.id]['action'] = 3
                await bot.send_message(message.chat.id, setting.COMMAND_WEATHER_SET_AUTO_NOTIFY_TIME_OK)
                await bot.send_message(message.chat.id, setting.COMMAND_WEATHER_SET_AUTO_NOTIFY_TIMEZONE)
            else:
                await bot.send_message(message.chat.id, setting.COMMAND_WEATHER_SET_AUTO_NOTIFY_TIME_ERROR)
        else:
            if validate_time(message.text, 'time'):
                channel.update({'auto_notify_time': message.text},
                               Query().channel_id == clients[message.chat.id]['channel_id'])
                clients[message.chat.id]['action'] = 3
                await bot.send_message(message.chat.id, setting.COMMAND_WEATHER_SET_AUTO_NOTIFY_TIME_OK)
                await bot.send_message(message.chat.id, setting.COMMAND_WEATHER_SET_AUTO_NOTIFY_TIMEZONE)
            else:
                await bot.send_message(message.chat.id, setting.COMMAND_WEATHER_SET_AUTO_NOTIFY_TIME_ERROR)
    elif clients[message.chat.id]['action'] == 3:
        if clients[message.chat.id]['type'] == 0:
            if validate_time(message.text, 'timezone'):
                user.update({'auto_notify_timezone': message.text},
                            Query().chat_id == message.chat.id)
                clients[message.chat.id]['action'] = 0
                await bot.send_message(message.chat.id, setting.COMMAND_WEATHER_SET_AUTO_NOTIFY_TIMEZONE_OK, reply_markup=types.ReplyKeyboardRemove())
            else:
                await bot.send_message(message.chat.id, setting.COMMAND_WEATHER_SET_AUTO_NOTIFY_TIMEZONE_ERROR)
        else:
            if validate_time(message.text, 'timezone'):
                channel.update({'auto_notify_timezone': message.text},
                               Query().channel_id == clients[message.chat.id]['channel_id'])
                clients[message.chat.id]['action'] = 0
                clients[message.chat.id]['type'] = 0
                clients[message.chat.id]['channel_id'] = 0
                await bot.send_message(message.chat.id, setting.COMMAND_WEATHER_SET_AUTO_NOTIFY_TIMEZONE_OK, reply_markup=types.ReplyKeyboardRemove())
            else:
                await bot.send_message(message.chat.id, setting.COMMAND_WEATHER_SET_AUTO_NOTIFY_TIMEZONE_ERROR)
    elif clients[message.chat.id]['action'] == 4:
        # Add group
        if validate_group(message):
            user.update({'groups': True},
                        Query().chat_id == message.chat.id)
            clients[message.chat.id]['action'] = 0
            await bot.send_message(message.chat.id, setting.COMMAND_WEATHER_SET_GROUP_OK, reply_markup=types.ReplyKeyboardRemove())
        else:
            await bot.send_message(message.chat.id, setting.COMMAND_WEATHER_SET_GROUP_ERROR)
    elif clients[message.chat.id]['action'] == 5:
        #get channel id by name
        clients[message.chat.id]['channel_id'] = channel.search((Query().name == message.text) & (Query().admin == message.chat.id) )[0]['channel_id']
        clients[message.chat.id]['action'] = 1
        await bot.send_message(message.chat.id, setting.COMMAND_WEATHER_SET_CITY)


def validate_group(message):
    data = message.forward_from_chat
    if data.type == 'channel':
        # add group to channel
        if not channel.search(Query().channel_id == message.chat.id):
            channel.insert(
                {'channel_id': data.id, 'name': data.title, 'admin': message.chat.id, 'city': '', 'country': '', 'auto_notify_time': '00:00', 'auto_notify_timezone': '+03:00'})
        return True
    else:
        return False


def get_weather_info(city, country):
    city = city.strip()
    country = country.strip()
    country = country.upper()
    data_city = owm.get_sity(city, country=country, matching='exact')

    weather = owm.get_weather_sity_coord(data_city['lat'], data_city['lon'])
    return weather


def setting_keyboard(chat_id, kit):
    if kit == 'main':
        markup = types.ReplyKeyboardMarkup(
            one_time_keyboard=True, resize_keyboard=True)
        markup.row('Установить город')
        markup.row('Добавить группу')
        if user.search(Query().chat_id == chat_id)[0]['groups']:
            markup.row('Настроить бота в группе')
        if user.search(Query().chat_id == chat_id)[0]['auto_notify']:
            markup.row('Отключить автоматическое уведомление')
            markup.row('Настроить автоматическое уведомление')
        else:
            markup.row('Включить автоматическое уведомление')
        return markup
    elif kit == 'cancel':
        markup = types.ReplyKeyboardMarkup(
            one_time_keyboard=True, resize_keyboard=True)
        markup.row('Отмена')
        return markup


def translate(text):
    return setting.WEATHER_CLOUDS[text]


def ucfirst(text):
    return text[0].upper() + text[1:]


def validate_time(time, type):
    if type == 'time':
        regex = r"^([01][0-9]|2[0-3]):([0-5][0-9])$"
        return re.match(regex, time)
    elif type == 'timezone':
        regex = r"^([+-][0-9]{2}):([0-9]{2})$"
        return re.match(regex, time)


def send_notification():
    """
    If the current time is equal to the user's time, send a notification
    """
    for user in user.all():
        if user.search(Query().chat_id == user['chat_id'])[0]['auto_notify']:
            time_zone = user.search(Query().chat_id == user['chat_id'])[
                0]['auto_notify_timezone']
            user_time = user.search(Query().chat_id == user['chat_id'])[
                0]['auto_notify_time']
            time_zone_offset = datetime.timedelta(
                hours=int(time_zone.split(':')[0]), minutes=int(time_zone.split(':')[1]))
            time = datetime.datetime.utcnow() + time_zone_offset
            time = time.strftime('%H:%M')
            if time == user_time:
                print('Send notification to ' + str(user['chat_id']))


def build_weather_data(city, country, type):
    weather_data = get_weather_info(city, country)
    if type == 1:
        data = 'Погода сейчас \n'
        data += 'Температура: ' + \
            str(weather_data['current']['temp']) + '°С \n'
        data += 'Влажность: ' + \
            str(weather_data['current']['humidity']) + '% \n'
        data += 'Погода: ' + \
            translate(weather_data['current']['weather'][0]['main']) + '\n'
        data += 'Описание: ' + \
            ucfirst(weather_data['current']['weather']
                    [0]['description']) + '\n'
        data += '\n'
        data += 'Погода днем' + '\n'
        data += 'Температура: ' + \
            str(weather_data['daily'][0]['temp']['day']) + '°С \n'
        data += 'Влажность: ' + \
            str(weather_data['daily'][0]['humidity']) + '% \n'
        data += 'Погода: ' + \
            translate(weather_data['daily'][0]['weather'][0]['main']) + '\n'
        data += 'Описание: ' + \
            ucfirst(weather_data['daily'][0]['weather']
                    [0]['description']) + '\n'
        data += 'Вероятность осадков: ' + \
            str(weather_data['daily'][0]['pop']*100) + '% \n'

    return data


asyncio.run(bot.polling(non_stop=True))
asyncio.run(send_notification())
