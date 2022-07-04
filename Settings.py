class Settings:

    TELEGRAM_BOT_TOKEN = ""
    WEATHER_API_KEY = ''
    WEATHER_EXCLUDE = 'minutely,hourly,alerts'
    WEATHER_UNITS = 'metric'
    WEATHER_LANG = 'ru'

    WEATHER_CLOUDS = {
        'Thunderstorm': 'Гроза',
        'Drizzle': 'Морось',
        'Rain': 'Дождь',
        'Snow': 'Снег',
        'Mist': 'Туман',
        'Smoke': 'Дымно',
        'Haze': 'Мгла',
        'Dust': 'Пыльно',
        'Clear': 'Ясно',
        'Clouds': 'Облачно'}


    WELCOME_MESSAGE = 'Привет! Я бот для получения информации о погоде. Напишите мне название города и страну, и я покажу погоду в этом городе.'

    ABOUT_MESSAGE = 'Автор Бота: https://t.me/Divarion_D\n'
    ABOUT_MESSAGE += 'GitHub: https://github.com/Divarion-D\n'

    COMMAND_SETTING = 'Выберите нужное действие:\n'

    COMMAND_WEATHER_SET_CITY = 'Введите название города и страну в формате: город, страна\n'
    COMMAND_WEATHER_SET_CITY += 'Например: London, US\n'
    COMMAND_WEATHER_SET_CITY += 'Можно получить по ссылке: https://openweathermap.org'

    COMMAND_WEATHER_SET_AUTO_NOTIFY_ON = 'Автоматическое уведомление включено'
    COMMAND_WEATHER_SET_AUTO_NOTIFY_OFF = 'Автоматическое уведомление выключено'

    COMMAND_WEATHER_SET_AUTO_NOTIFY_TIME = 'Введите время в которое будет прихоить сводка в формате: часы:минуты\n'
    COMMAND_WEATHER_SET_AUTO_NOTIFY_TIME_OK = 'Время установлено'
    COMMAND_WEATHER_SET_AUTO_NOTIFY_TIME_ERROR = 'Неверное время'

    COMMAND_WEATHER_SET_AUTO_NOTIFY_TIMEZONE = 'Введите Часовой пояс по UTC\n'
    COMMAND_WEATHER_SET_AUTO_NOTIFY_TIMEZONE += 'Пример: +04:00\n'
    COMMAND_WEATHER_SET_AUTO_NOTIFY_TIMEZONE_OK = 'Часовой пояс установлен'
    COMMAND_WEATHER_SET_AUTO_NOTIFY_TIMEZONE_ERROR = 'Неверный часовой пояс'

    COMMAND_WEATHER_SET_GROUP_ADD = 'Добавьте меня в группу\n'
    COMMAND_WEATHER_SET_GROUP_ADD += 'После чего перешлите мне сообщение из этой группы'
    COMMAND_WEATHER_SET_GROUP_OK = 'Я добавлен в группу'
    COMMAND_WEATHER_SET_GROUP_ERROR = 'Не удалось добавить меня в группу'

    COMMAND_WEATHER_SET_CITY_OK = 'Город изменен'
    
    COMMAND_WEATHER_SET_CANCEL = 'Отмена'
