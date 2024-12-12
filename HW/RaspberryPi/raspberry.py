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
    """Load the lighting configuration JSON file."""
    try:
        with open(JSON_FILE_PATH, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Error: Configuration file '{JSON_FILE_PATH}' not found.")
        return {}
    except json.JSONDecodeError:
        print(f"Error: Configuration file '{JSON_FILE_PATH}' contains invalid JSON.")
        return {}

def save_lighting_config(config):
    """Save the lighting configuration JSON file."""
    try:
        with open(JSON_FILE_PATH, "w") as file:
            json.dump(config, file, indent=4)
    except Exception as e:
        print(f"Error: Failed to save lighting configuration - {e}")

def apply_lighting(class_type):
    """Apply lighting based on the provided class type."""
    global current_state
    config = load_lighting_config()  # Load lighting configuration

    # Retrieve settings for the given class
    if str(class_type) in config:
        settings = config[str(class_type)]
        brightness = settings.get("lx", 1.0)
        color = (settings.get("r", 255), settings.get("g", 255), settings.get("b", 255))

def apply_lighting(class_type):
    """Apply lighting based on the provided class type."""
    global current_state
    config = load_lighting_config()

    # Retrieve settings for the given class
    if str(class_type) in config:
        settings = config[str(class_type)]
        brightness = settings.get("lx", 1.0)
        color = (settings.get("r", 255), settings.get("g", 255), settings.get("b", 255))

        # Avoid redundant updates
        if current_state["lx"] != brightness or current_state["color"] != color:
            print(f"Applying lighting for class {class_type}: {settings}")
            set_brightness(brightness)
            set_color(color)
            current_state = {"lx": brightness, "color": color}
    else:
        print(f"Class type {class_type} not found in configuration. Turning off lights.")
        turn_off()

# MQTT handlers
def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    client.publish(TOPIC_PUBLISH, "!", retain=True)
    client.subscribe(TOPIC_SUBSCRIBE_LIGHT)
    client.subscribe(TOPIC_SUBSCRIBE_SCENARIO)

def on_message(client, userdata, msg):
    global current_state
    print(f"Message received from app: {msg.payload.decode()}")
    try:
        data = json.loads(msg.payload.decode())
        if msg.topic == TOPIC_SUBSCRIBE_LIGHT:
            # Update NeoPixel directly
            lx = data.get("lx", 1.0)
            r = data.get("r", 255)
            g = data.get("g", 255)
            b = data.get("b", 255)
            print(f"Updating light: lx={lx}, color=({r}, {g}, {b})")
            set_brightness(lx)
            set_color((r, g, b))
            current_state = {"lx": lx, "color": (r, g, b)}
        elif msg.topic == TOPIC_SUBSCRIBE_SCENARIO:
            # Update configuration file
            class_type = str(data.get("class"))
            lx = data.get("lx", 1.0)
            r = data.get("r", 255)
            g = data.get("g", 255)
            b = data.get("b", 255)
            config = load_lighting_config()
            config[class_type] = {"lx": lx, "r": r, "g": g, "b": b}
            save_lighting_config(config)
            print(f"Updated scenario for class {class_type}: {config[class_type]}")
    except json.JSONDecodeError:
        print("Error: Received data is not valid JSON.")

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
