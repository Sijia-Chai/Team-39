#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests

NOAA_api_token = 'htOHiXdrJuOvOCiePVaHwviVwfKwRuRY'

# NOAA API endpoint for daily summaries
endpoint = f'https://www.ncdc.noaa.gov/cdo-web/api/v2/data?datasetid=GHCND&stationid=GHCND:USW00094728&startdate=2023-10-01&enddate=2023-10-03&units=standard'

# Add the API token to the request headers
headers = {
    'token': NOAA_api_token
}

# Make the API request
response = requests.get(endpoint, headers=headers)

# Check if the request was successful
if response.status_code == 200:
    data = response.json()
    # Extract and use the relevant daily weather data from 'data'
    print(data)
else:
    print(f"Error: {response.status_code} - {response.text}")


Eventbrite_api_token = 'HIVMDJ4BER24AE5B4TLW'