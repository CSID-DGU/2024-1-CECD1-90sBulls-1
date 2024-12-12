import board
import neopixel
import socket
import json
import asyncio
import time
import paho.mqtt.client as mqtt

# Server configuration
SERVER_IP = '211.188.63.60'
SERVER_PORT = 8080

# MQTT configuration
BROKER = "localhost"
PORT = 1883
TOPIC_SUBSCRIBE_LIGHT = "app/light"
TOPIC_SUBSCRIBE_SCENARIO = "app/scenario"
TOPIC_PUBLISH = "pi/light"

# File path for lighting configuration
JSON_FILE_PATH = "lighting_config.json"

# NeoPixel strip configuration
STRIPS_CONFIG = [
    {"pin": board.D18, "num_leds": 45},
    {"pin": board.D21, "num_leds": 45},
    {"pin": board.D12, "num_leds": 45}
]

# Create NeoPixel objects
strips = [
    neopixel.NeoPixel(config["pin"], config["num_leds"], auto_write=False)
    for config in STRIPS_CONFIG
]

# Current state caching to avoid redundant updates
current_state = {"lx": None, "color": (None, None, None)}

def set_color(color):
    """Set the color for all NeoPixel strips."""
    for strip in strips:
        strip.fill(color)
        strip.show()

def set_brightness(brightness):
    """Set the brightness for all NeoPixel strips."""
    for strip in strips:
        strip.brightness = brightness
        strip.show()

def turn_off():
     """Turn off all NeoPixel strips."""
    for strip in strips:
        strip.fill((0, 0, 0))
        strip.show()

def load_lighting_config():
    try:
        with open(JSON_FILE_PATH, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Error: Configuration file '{JSON_FILE_PATH}' not found.")
        return {}
    except json.JSONDecodeError:
        print(f"Error: Configuration file '{JSON_FILE_PATH}' contains invalid JSON.")
        return {}
