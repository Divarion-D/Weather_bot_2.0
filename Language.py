class Language:
    CLOUDS = {
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

    WELCOME_MESSAGE = 'Привет! Я бот для получения информации о погоде. Напиши /help получения всех команд.'

    ABOUT_MESSAGE = 'Автор Бота: https://t.me/Divarion_D\n'
    ABOUT_MESSAGE += 'GitHub: https://github.com/Divarion-D\n'

    SETTING = 'Выберите нужное действие:\n'
    SETUP_CHANNEL = 'Выберете нужное действие для настройки бота в канале:\n'

    SET_CITY = 'Введите название города и страну в формате: город, страна\n'
    SET_CITY += 'Например: London, US\n'
    SET_CITY += 'Можно получить по ссылке: https://openweathermap.org'
    SET_CITY_OK = 'Город изменен'

    AUTO_NOTIFY_ON = 'Автоматическое уведомление включено'
    AUTO_NOTIFY_OFF = 'Автоматическое уведомление выключено'

    SET_AUTO_NOTIFY_TIME = 'Введите время в которое будет прихоить сводка в формате: часы:минуты\n'
    SET_AUTO_NOTIFY_TIME_OK = 'Время установлено'
    SET_AUTO_NOTIFY_TIME_ERROR = 'Неверное время'

    SET_TIMEZONE = 'Введите Часовой пояс по UTC\n'
    SET_TIMEZONE += 'Пример: +04:00\n'
    SET_TIMEZONE_OK = 'Часовой пояс установлен'
    SET_TIMEZONE_ERROR = 'Неверный часовой пояс'

    ADD_CHANNEL = 'Добавьте меня в канал\n'
    ADD_CHANNEL += 'После чего перешлите мне сообщение из этого канала'
    ADD_CHANNEL_OK = 'Я добавлен в канал'
    ADD_CHANNEL_ERROR = 'Не удалось добавить меня в канал'

    MY_CHANNEL = 'Выберете один из каналов для настройки: '

    HELP_MESSAGE = 'Помощь:\n'
    HELP_MESSAGE += '/start - Приветствие\n'
    HELP_MESSAGE += '/help - Помощь\n'
    HELP_MESSAGE += '/about - О боте\n'
    HELP_MESSAGE += '/settings - Настройки\n'
    HELP_MESSAGE += '/weather - Погода\n'
    
    SET_CANCEL = 'Отмена'