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

def get_weather_description(weather_code):
    if weather_code in [0]:
        return "Clear sky"
    elif weather_code in [1]:
        return "Mainly clear"
    elif weather_code in [2]:
        return "Partly cloudy"
    elif weather_code in [3]:
        return "Overcast"
    elif weather_code in [45, 48]:
        return "Fog"
    elif weather_code in [51, 61, 80]:
        return "Light rain"
    elif weather_code in [53, 63, 81]:
        return "Moderate rain"
    elif weather_code in [55, 65, 82]:
        return "Heavy rain"
    elif weather_code in [95]:
        return "Thunderstorm"
    elif weather_code in [99]:
        return "Severe thunderstorm"
    else:
        return "Unknown weather condition"

def get_weather_image(weather_code):
    """Map weather codes to image filenames."""
    if weather_code in [0]:
        return "00.bmp"  # Clear sky
    elif weather_code in [1]:
        return "01.bmp"  # Mainly clear
    elif weather_code in [2, 3]:
        return "02.bmp"  # Partly cloudy or overcast
    elif weather_code in [45, 48]:
        return "57.bmp"  # Fog
    elif weather_code in [51, 61, 80]:
        return "09.bmp"  # Light rain
    elif weather_code in [53, 63, 81]:
        return "10.bmp"  # Moderate rain
    elif weather_code in [55, 65, 82]:
        return "12.bmp"  # Heavy rain
    elif weather_code in [95]:
        return "21.bmp"  # Thunderstorm
    elif weather_code in [99, 25]:
        return "25.bmp"  # Severe thunderstorm
    else:
        return "99.bmp"  # Unknown or N/A
    
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
        
        # Get weather description using the function
        weather_description = get_weather_description(weather_state)
        
        # Return structured data
        return {
            "temperature": temperature,
            "weather_code": weather_state,
            "weather_description": weather_description
        }
    
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching weather data: {e}")
        return None

def display_weather(epd, font, latitude, longitude):
    try:
        # Fetch weather data
        weather_data = get_weather(latitude, longitude)
        if not weather_data:
            return
        
        # Extract data
        temperature = weather_data["temperature"]
        weather_code = weather_data["weather_code"]
        weather_description = weather_data["weather_description"]
        
        # Get the corresponding image filename
        weather_image = get_weather_image(weather_code)
        
        # Create a new image for the e-ink display
        Himage = Image.new('1', (epd.width, epd.height), 255)  # 255: clear the frame
        draw = ImageDraw.Draw(Himage)
        
        # Draw the weather information text
        draw.text((10, 10), "Weather in Porto:", font=font, fill=0)
        draw.text((10, 50), f"Temperature: {temperature}°C", font=font, fill=0)
        draw.text((10, 90), f"Condition: {weather_description}", font=font, fill=0)
        
        # Load the weather image
        weather_image_path = os.path.join(picdir, weather_image)
        weather_icon = Image.open(weather_image_path)
        
        # Paste the weather image onto the main image
        Himage.paste(weather_icon, (10, 130))  # Adjust position as needed
        
        # Display the combined image on the e-ink screen
        epd.display_4GRAY(epd.getbuffer_4Gray(Himage))
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
