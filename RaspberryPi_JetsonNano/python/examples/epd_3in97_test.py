#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys
import os
picdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'pic')
libdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'lib')
if os.path.exists(libdir):
    sys.path.append(libdir)

import logging
from waveshare_epd import epd3in97
import time
from PIL import Image,ImageDraw,ImageFont
import traceback
import requests

logging.basicConfig(level=logging.DEBUG)



def get_weather(latitude, longitude):
    try:
        # Open-Meteo API endpoint
        url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current_weather=true"
        
        # Make the API request
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad responses
        
        # Parse the JSON response
        data = response.json()
        current_weather = data.get("current_weather", {})
        
        # Extract temperature and weather state
        temperature = current_weather.get("temperature")
        weather_state = current_weather.get("weathercode")
        
        # Map weather codes to descriptions (simplified example)
        weather_descriptions = {
            0: "Clear sky",
            1: "Mainly clear",
            2: "Partly cloudy",
            3: "Overcast",
            45: "Fog",
            48: "Depositing rime fog",
            51: "Drizzle: Light",
            53: "Drizzle: Moderate",
            55: "Drizzle: Dense",
            61: "Rain: Slight",
            63: "Rain: Moderate",
            65: "Rain: Heavy",
            80: "Rain showers: Slight",
            81: "Rain showers: Moderate",
            82: "Rain showers: Violent",
            95: "Thunderstorm: Slight or moderate",
            99: "Thunderstorm: Heavy hail"
        }
        
        weather_description = weather_descriptions.get(weather_state, "Unknown weather condition")
        
        return f"Temperature: {temperature}°C, Weather: {weather_description}"
    
    except requests.exceptions.RequestException as e:
        return f"Error fetching weather data: {e}"

# Add this function to fetch and display weather data
def display_weather(epd, font, latitude, longitude):
    try:
        # Fetch weather data
        weather_info = get_weather(latitude, longitude)
        
        # Create a new image for the e-ink display
        Himage = Image.new('1', (epd.width, epd.height), 255)  # 255: clear the frame
        draw = ImageDraw.Draw(Himage)
        
        # Draw the weather information
        draw.text((10, 10), "Weather in Porto:", font=font, fill=0)
        draw.text((10, 50), weather_info, font=font, fill=0)
        
        # Display the image on the e-ink screen
        epd.display(epd.getbuffer(Himage))
        time.sleep(2)
    except Exception as e:
        logging.error(f"Error displaying weather: {e}")

# Main program
try:
    logging.info("epd3in97 Demo")
    epd = epd3in97.EPD()
    
    logging.info("init and Clear")
    epd.init()
    epd.Clear()
    
    # Replace the latitude and longitude with Porto's coordinates
    latitude = 41.1579
    longitude = -8.6291

    # Call the function to display weather data
    font24 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 24)
    display_weather(epd, font24, latitude, longitude)
    
    # logging.info("Clear...")
    # epd.init()
    # epd.Clear()
    
    logging.info("Goto Sleep...")
    epd.sleep()
        
except IOError as e:
    logging.info(e)
    
except KeyboardInterrupt:    
    logging.info("ctrl + c:")
    epd3in97.epdconfig.module_exit(cleanup=True)
    exit()
