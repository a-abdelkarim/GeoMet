from decouple import config
import requests

class Weather:
    
    def __init__(self, api_key=config('WEATHER_KEY', default='207580c5db2a4e30b49102357231709')):
        self.api_key = api_key
    
    def get_current(self, lat=None, lon=None):
        if not lat or not lon:
            raise ValueError("Please provide valid lat and lon")
        
        url = f"{config('WEATHER_URL', default='https://api.weatherapi.com/v1/')}current.json"
        params = {"key": self.api_key,"q": f"{lon},{lat}"}
        
        req = requests.get(url=url, params=params)
        return req.json()
    
    def get_forecast(self):
        pass
    
    def get_future(self):
        pass
    

if __name__ == '__main__':
    weather = Weather()
    current_weather = weather.get_current(30.981392752866526,30.04915977138353)