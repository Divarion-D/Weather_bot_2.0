import requests

from Settings import Settings
from Language import Language

setting = Settings()
language = Language()

class OWM:
    def __init__(self, api_key, exclude, units, lang):
        self.api_key = api_key
        self.exclude = exclude
        self.units = units
        self.lang = lang
        self.base_url = 'http://api.openweathermap.org/data/2.5/'

    def get_sity(self, city, country, matching='exact'):
        '''
        Получает данные о городе из базы данных по его названию
        '''
        url = f'{self.base_url}find?q={city},{country}&type={matching}'
        response = requests.get(
            url, params={'appid': self.api_key}).json()['list'][0]

        return {
            'id': response['id'],
            'city': response['name'],
            'country': response['sys']['country'],
            'lat': response['coord']['lat'],
            'lon': response['coord']['lon'],
        }

    def get_weather_sity_id(self, city_id):
        url = f'{self.base_url}weather?id={str(city_id)}'
        return requests.get(url, params={'appid': self.api_key}).json()

    def get_weather_sity_name(self, city, country):
        url = f'{self.base_url}weather?q={city},{country}'
        return requests.get(url, params={'appid': self.api_key}).json()

    def get_weather_sity_coord(self, lat, lon):
        '''
        Получает данные о погоде по координатам
        '''
        parameter = f'&units={self.units}&lang={self.lang}&exclude={self.exclude}'

        url = f'{self.base_url}onecall?lat={str(lat)}&lon={str(lon)}{parameter}'

        return requests.get(url, params={'appid': self.api_key}).json()

    def get_weather_info(self, city, country):
        '''
        Получает данные о погоде по названию города
        '''
        city = city.strip()
        country = country.strip().upper()
        data_city = self.get_sity(city, country=country, matching='exact')
        return self.get_weather_sity_coord(data_city['lat'], data_city['lon'])

    def build_weather_data(self, city, country, type):
        '''
        Форматирует данные о погоде по названию города
        '''
        weather_data = self.get_weather_info(city, country)
        if type == 1:
            data = 'Погода сейчас \n'
            data += 'Температура: ' + \
                str(weather_data['current']['temp']) + '°С \n'
            data += 'Влажность: ' + \
                str(weather_data['current']['humidity']) + '% \n'
            data += 'Погода: ' + \
                self.weather_translate(weather_data['current']
                                       ['weather'][0]['main']) + '\n'
            data += 'Описание: ' + \
                self.ucfirst(weather_data['current']['weather']
                             [0]['description']) + '\n'
            data += '\n'
            data += 'Погода днем' + '\n'
            data += 'Температура: ' + \
                str(weather_data['daily'][0]['temp']['day']) + '°С \n'
            data += 'Влажность: ' + \
                str(weather_data['daily'][0]['humidity']) + '% \n'
            data += 'Погода: ' + \
                self.weather_translate(weather_data['daily']
                                       [0]['weather'][0]['main']) + '\n'
            data += 'Описание: ' + \
                self.ucfirst(weather_data['daily'][0]['weather']
                             [0]['description']) + '\n'
            data += 'Вероятность осадков: ' + \
                str(weather_data['daily'][0]['pop']*100) + '% \n'

        return data

    def weather_translate(self, text):
        ''' 
        Переводит название погоды на другой язык
        '''
        return language.CLOUDS[text]

    def ucfirst(self, text):
        '''
        Переводит первую букву в верхний регистр
        '''
        return text[0].upper() + text[1:]
