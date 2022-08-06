# Погодный бот
## Описание
Телеграм бот для получения погоды из OpenWeatherMap

### Реализованно
- [x] Получение погоды по команде
- [x] Поддержка каналов
- [x] Автоматическое уведомление
- [x] Установка времени для уведомлений
- [x] Установка часового пояса по UTC
- [ ] Графики
- [ ] Выбор типа погодных уведомлений
- [ ] Конструктор погодных уведомлений

## Как развернуть проект

#### Развертывание на Heroku
[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://dashboard.heroku.com/new?template=https://github.com/Divarion-D/Weather_bot_2.0)

#### Развертывание на VPS
 ```
git clone https://github.com/Divarion-D/Weather_bot_2.0
cd Weather_bot_2.0
python3 -m venv venv
source venv/bin/activate
export TG_BOT_TOKEN=Your Bot Token
export OW_TOKEN=Your OpenWeatherMap Token
pip3 install -r requirements.txt
python main.py
```

## Немного информации

Пример погодного отчета:

```
Погода сейчас 
Температура: 28.35°С 
Влажность: 32% 
Погода: Ясно
Описание: Ясно

Погода днем
Температура: 29.12°С 
Влажность: 30% 
Погода: Ясно
Описание: Ясно
Вероятность осадков: 0%
```