import board
import neopixel
import socket
import json
import asyncio
import time
import paho.mqtt.client as mqtt


SERVER_IP = '211.188.63.60'
SERVER_PORT = 8080

BROKER = "localhost"
PORT = 1883
TOPIC_SUBSCRIBE_LIGHT = "app/light"
TOPIC_SUBSCRIBE_SCENARIO = "app/scenario"
TOPIC_PUBLISH = "pi/light"
