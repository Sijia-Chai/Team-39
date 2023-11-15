import requests
import json

weather_key = "e841e7921b15804eaae940ab17328077"

def call_weather_api(location: str):
  api_url = 'https://api.openweathermap.org/data/2.5/weather?q='+location+'&APPID='+weather_key+'&units=imperial'
  return requests.get(api_url)

# Weather API

@app.route("/weather", methods=['GET'])
def weather():
    return render_template('weather.html', supress='True')

@app.route('/weather', methods=['POST'])
def getWeather():
    if request.method == 'POST':
        response = call_weather_api(request.form.get('city'))
    # checking the status code of the request
        if response.status_code == 200:
            return render_template('weather_ret.html', city=request.form.get('city'), temperature=response.json()['main']['temp'], feels_like=response.json()['main']['feels_like'])
        else:
            # showing the error message
            return render_template('weather.html') + "<h3 style = \"color: #ff0000\">An error occured loading up the weather for the city provided</h3>"
