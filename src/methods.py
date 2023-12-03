import requests
import json

google_maps_key = 'secret'
weather_key = 'secret'

def call_weather_api(location: str):
  return requests.get('https://api.openweathermap.org/data/2.5/weather?q='+location+'&APPID='+weather_key+'&units=imperial')

def call_map_api(location: str):
    response = json.loads(requests.get("https://maps.googleapis.com/maps/api/place/textsearch/json?query="+("fun things to do in "+ location)+"&key="+google_maps_key).text)['results']
    List = []
    for entry in response:
        Dict = {}
        Dict['name'] = entry['name']
        Dict['address'] = entry['formatted_address']
        Dict['rating'] = entry['rating']
        tmp = ""
        for i in entry['types']:
            tmp += i + ", "
        Dict['category'] = tmp.replace("_"," ")[:-2]
        List.append(Dict)
    return json.loads(json.dumps(List))
