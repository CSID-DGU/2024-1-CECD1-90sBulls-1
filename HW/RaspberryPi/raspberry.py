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

STRIPS_CONFIG = [
    {"pin": board.D18, "num_leds": 45},
    {"pin": board.D21, "num_leds": 45},
    {"pin": board.D12, "num_leds": 45}
]
