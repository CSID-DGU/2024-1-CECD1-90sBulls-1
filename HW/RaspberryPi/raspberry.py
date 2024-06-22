import board
import neopixel
import socket
import json

class NeoPixelStrip:
    def __init__(self, pin, num_leds):
        self.strip = neopixel.NeoPixel(pin, num_leds, auto_write=False)

    def set_color(self, color):
        self.strip.fill(color)
        self.strip.show()

    def set_brightness(self, brightness):
        self.strip.brightness = brightness
        self.strip.show()

    def turn_off(self):
        self.strip.fill((0, 0, 0))
        self.strip.show()

class NeoPixelController:
    def __init__(self, strips_config):
        self.strips = [NeoPixelStrip(config["pin"], config["num_leds"]) for config in strips_config]

    def set_color(self, color):
        for strip in self.strips:
            strip.set_color(color)
    
    def set_brightness(self, brightness):
        for strip in self.strips:
            strip.set_brightness(brightness)

    def turn_off(self):
        for strip in self.strips:
            strip.turn_off()

    @staticmethod
    def normalization_lux(lx):
        return lx * 0.01


class ServerClient:
    def __init__(self, server_ip, server_port, controller):
        self.server_ip = server_ip
        self.server_port = server_port
        self.controller = controller

    def receive_data(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self.server_ip, self.server_port))
            while True:
                data = s.recv(1024)
                if not data:
                    break
                print(f"Data received from server: {data.decode()}")
                try:
                    data_json = json.loads(data.decode())
                    brightness = data_json['lx']
                    color_r = data_json['r']
                    color_g = data_json['g']
                    color_b = data_json['b']

                    # Set brightness and color temperature
                    self.controller.set_brightness(NeoPixelController.normalization_lux(brightness))
                    self.controller.set_color((color_r, color_g, color_b))
                except json.JSONDecodeError:
                    print("Received data is not valid JSON.")


if __name__ == "__main__":
    SERVER_IP = '110.234.18.234'
    SERVER_PORT = 8080
    
    STRIPS_CONFIG = [
        {"pin": board.D18, "num_leds": 12},
        {"pin": board.D21, "num_leds": 12},
        {"pin": board.D12, "num_leds": 12}
    ]

    controller = NeoPixelController(STRIPS_CONFIG)
    client = ServerClient(SERVER_IP, SERVER_PORT, controller)

    try:
        client.receive_data()
    except KeyboardInterrupt:
        controller.turn_off()  # Turn off the strips on exit
 
