from ctypes import resize
from telebot.async_telebot import AsyncTeleBot, types
import re
import datetime
import pytz
import asyncio
import timedelta
from Settings import Settings
from tinydb import Query, TinyDB
from Openweather import OWM

db = TinyDB('db.json')
setting = Settings()

bot = AsyncTeleBot(setting.TELEGRAM_BOT_TOKEN, parse_mode=None)
owm = OWM(setting.WEATHER_API_KEY, setting.WEATHER_EXCLUDE,
          setting.WEATHER_UNITS, setting.WEATHER_LANG)

clients = {}


@bot.message_handler(commands=['start'])
async def start_message(message):

    print(message.chat.type)
    
    # add chat_id to db
    if not db.search(Query().chat_id == message.chat.id):
        db.insert({'chat_id': message.chat.id, 'city': '', 'country': '',
                  'auto_notify': False, 'auto_notify_time': '00:00', 'auto_notify_timezone': '+03:00'})

    await bot.send_message(message.chat.id, setting.WELCOME_MESSAGE)


@bot.message_handler(commands=['about'])
async def about_message(message):
    await bot.send_message(message.chat.id, setting.ABOUT_MESSAGE)


@bot.message_handler(commands=['weather'])
async def weather_message(message):
    city = db.search(Query().chat_id == message.chat.id)[0]['city']
    country = db.search(Query().chat_id == message.chat.id)[0]['country']
    if city == '' or country == '':
        clients[message.chat.id] = 1
        markup = setting_keyboard(message.chat.id, 'cancel')
        await bot.send_message(message.chat.id, setting.COMMAND_WEATHER_SET_CITY, reply_markup=markup)
        return
    await bot.send_message(message.chat.id, build_weather_data(city, country, 1))


@bot.message_handler(commands=['settings'])
async def settings_message(message):
    # Send a message and wait for a response
    markup = setting_keyboard(message.chat.id, 'main')
    await bot.send_message(message.chat.id, setting.COMMAND_WEATHER_SETTING, reply_markup=markup)


@bot.message_handler(func=lambda message: True)
async def echo_all(message):

    if message.text.lower() == 'установить город':
        # Set city and country
        clients[message.chat.id] = 1
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        markup.row('Отмена')
        await bot.send_message(message.chat.id, setting.COMMAND_WEATHER_SET_CITY, reply_markup=markup)
    elif message.text.lower() == 'включить автоматическое уведомление':
        # Set auto notify
        db.update({'auto_notify': True}, Query().chat_id == message.chat.id)
        markup = setting_keyboard(message.chat.id, 'main')
        await bot.send_message(message.chat.id, setting.COMMAND_WEATHER_SET_AUTO_NOTIFY_ON, reply_markup=markup)
    elif message.text.lower() == 'отключить автоматическое уведомление':
        # Set auto notify
        db.update({'auto_notify': False}, Query().chat_id == message.chat.id)
        markup = setting_keyboard(message.chat.id, 'main')
        await bot.send_message(message.chat.id, setting.COMMAND_WEATHER_SET_AUTO_NOTIFY_OFF, reply_markup=markup)
    elif message.text.lower() == 'отмена':
        # Cancel
        clients[message.chat.id] = 0
        await bot.send_message(message.chat.id, setting.COMMAND_WEATHER_SET_CANCEL, reply_markup=types.ReplyKeyboardRemove())
    elif message.text.lower() == 'настроить автоматическое уведомление':
        # Setting auto notify
        clients[message.chat.id] = 2
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        markup.row('Отмена')
        await bot.send_message(message.chat.id, setting.COMMAND_WEATHER_SET_AUTO_NOTIFY_TIME, reply_markup=markup)
    elif clients[message.chat.id] == 1:
        # Set city and country
        data = message.text.split(',')
        db.update({'city': data[0], 'country': data[1]}, Query().chat_id == message.chat.id)
        clients[message.chat.id] = 0
        await bot.send_message(message.chat.id, setting.COMMAND_WEATHER_SET_CITY_OK, reply_markup=types.ReplyKeyboardRemove())
    elif clients[message.chat.id] == 2:
        # Set time for auto notify
        if validate_time(message.text, 'time'):
            db.update({'auto_notify_time': message.text}, Query().chat_id == message.chat.id)
            clients[message.chat.id] = 3
            await bot.send_message(message.chat.id, setting.COMMAND_WEATHER_SET_AUTO_NOTIFY_TIME_OK)
            # set timezone for auto notify
            await bot.send_message(message.chat.id, setting.COMMAND_WEATHER_SET_AUTO_NOTIFY_TIMEZONE)
        else:
            await bot.send_message(message.chat.id, setting.COMMAND_WEATHER_SET_AUTO_NOTIFY_TIME_ERROR)
    elif clients[message.chat.id] == 3:
        # Set timezone for auto notify
        if validate_time(message.text, 'timezone'):
            db.update({'auto_notify_timezone': message.text}, Query().chat_id == message.chat.id)
            clients[message.chat.id] = 0
            await bot.send_message(message.chat.id, setting.COMMAND_WEATHER_SET_AUTO_NOTIFY_TIMEZONE_OK, reply_markup=types.ReplyKeyboardRemove())
        else:
            await bot.send_message(message.chat.id, setting.COMMAND_WEATHER_SET_AUTO_NOTIFY_TIMEZONE_ERROR)

def get_weather_info(city, country):
    city = city.strip()
    country = country.strip()
    country = country.upper()
    data_city = owm.get_sity(city, country=country, matching='exact')

    weather = owm.get_weather_sity_coord(data_city['lat'], data_city['lon'])
    return weather

def setting_keyboard(chat_id, kit):
    if kit == 'main':
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        markup.row('Установить город')
        if db.search(Query().chat_id == chat_id)[0]['auto_notify']:
            markup.row('Отключить автоматическое уведомление')
            markup.row('Настроить автоматическое уведомление')
        else:
            markup.row('Включить автоматическое уведомление')
        return markup
    elif kit == 'cancel':
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
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

# Send notification to all users if time matches UTC correction
def send_notification():
    for user in db.all():
        if db.search(Query().chat_id == user['chat_id'])[0]['auto_notify']:
            time_zone = db.search(Query().chat_id == user['chat_id'])[0]['auto_notify_timezone']
            user_time = db.search(Query().chat_id == user['chat_id'])[0]['auto_notify_time']
            time_zone_offset = datetime.timedelta(hours=int(time_zone.split(':')[0]), minutes=int(time_zone.split(':')[1]))
            time = datetime.datetime.utcnow() + time_zone_offset
            time = time.strftime('%H:%M')
            if time == user_time:
                print('Send notification to ' + str(user['chat_id']))

def build_weather_data(city, country, type):
    weather_data = get_weather_info(city, country)
    if type == 1:
        data = 'Погода сейчас \n'
        data += 'Температура: ' + str(weather_data['current']['temp']) + '°С \n'
        data += 'Влажность: ' + str(weather_data['current']['humidity']) + '% \n'
        data += 'Погода: ' + \
            translate(weather_data['current']['weather'][0]['main']) + '\n'
        data += 'Описание: ' + \
            ucfirst(weather_data['current']['weather'][0]['description']) + '\n'
        data += '\n'
        data += 'Погода днем' + '\n'
        data += 'Температура: ' + \
            str(weather_data['daily'][0]['temp']['day']) + '°С \n'
        data += 'Влажность: ' + str(weather_data['daily'][0]['humidity']) + '% \n'
        data += 'Погода: ' + \
            translate(weather_data['daily'][0]['weather'][0]['main']) + '\n'
        data += 'Описание: ' + \
            ucfirst(weather_data['daily'][0]['weather'][0]['description']) + '\n'
        data += 'Вероятность осадков: ' + \
            str(weather_data['daily'][0]['pop']*100) + '% \n'

    return data

asyncio.run(bot.polling(non_stop=True))
asyncio.run(send_notification())
