import board
import neopixel
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
 
