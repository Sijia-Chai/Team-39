from flask import Flask, render_template, request
import requests
import json

app = Flask(__name__)

# Replace these with your own API keys
OPENWEATHERMAP_API_KEY = 'e841e7921b15804eaae940ab17328077'
EVENTBRITE_API_KEY = 'HIVMDJ4BER24AE5B4TLW'

# Home route
@app.route('/')
def home():
    return render_template('index.html')

# Recommendation route
@app.route('/recommendation', methods=['POST'])
def recommendation():
    city = request.form['city']

    # Get weather information from OpenWeatherMap
    weather_url = 'http://api.openweathermap.org/data/2.5/weather?q=' + city + '&appid=' + OPENWEATHERMAP_API_KEY
    weather_response = requests.get(weather_url)
    weather_data = weather_response.json()

    # Get events from Eventbrite
    eventbrite_url = 'https://www.eventbriteapi.com/v3/events/search/?q=' + city + '&token=' + EVENTBRITE_API_KEY
    eventbrite_response = requests.get(eventbrite_url)
    eventbrite_data = eventbrite_response.json()

    # Process data and generate recommendations
    indoor_events = []
    outdoor_events = []

    if 'weather' in weather_data and 'main' in weather_data['weather'][0]:
        weather_condition = weather_data['weather'][0]['main'].lower()

        # Recommend indoor events for rainy weather
        if 'rain' in weather_condition:
            indoor_events = [event['name']['text'] for event in eventbrite_data.get('events', [])]

        # Recommend outdoor events for non-rainy weather
        else:
            outdoor_events = [event['name']['text'] for event in eventbrite_data.get('events', [])]

    return render_template('index.html', city=city, indoor_events=indoor_events, outdoor_events=outdoor_events)

if __name__ == '__main__':
    app.run(debug=True)
