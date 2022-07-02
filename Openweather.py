import requests

class OWM:
    def __init__(self, api_key, exclude, units, lang):
        self.api_key = api_key
        self.exclude = exclude
        self.units = units
        self.lang = lang
        self.base_url = 'http://api.openweathermap.org/data/2.5/'
    
    def get_sity(self, city, country, matching='exact'):
        url = self.base_url + 'find?q=' + city + ',' + country + '&type=' + matching
        response = requests.get(url, params={'appid': self.api_key}).json()['list'][0]

        data = {
            'id': response['id'],
            'city': response['name'],
            'country': response['sys']['country'],
            'lat': response['coord']['lat'],
            'lon': response['coord']['lon'],
        }
        return data
    
    def get_weather_sity_id(self, city_id):
        url = self.base_url + 'weather?id=' + str(city_id)
        response = requests.get(url, params={'appid': self.api_key}).json()
        return response
    
    def get_weather_sity_name(self, city, country):
        url = self.base_url + 'weather?q=' + city + ',' + country
        response = requests.get(url, params={'appid': self.api_key}).json()
        return response
    
    def get_weather_sity_coord(self, lat, lon):
        parameter = '&units=' + self.units + '&lang=' + self.lang + '&exclude=' + self.exclude
        url = self.base_url + 'onecall?lat=' + str(lat) + '&lon=' + str(lon) + parameter
        response = requests.get(url, params={'appid': self.api_key}).json()
        return response