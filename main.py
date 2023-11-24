import time
from machine import Pin
from neopixel import NeoPixel
import ntptime
from random import randint

from logging import Logger
from networking import Client
from networking import ConnectionError


MATRIX_PIN = 32
UTC_OFFSET = 0 * 60 * 60


class Led():
    def __init__(self, num, np):
        self.np = np
        self.num = num
        self.value = [0, 0, 0]
        self.decrease = False

    def set_color(self, color=[20, 20, 20]):
        self.value = color
        self.np[self.num] = self.value
        self.np.write()

    def increase_brightness_red(self, steps=1):
        self.value[0] = self.value[0] + steps
        self.np[self.num] = self.value
        self.np.write()

    def decrease_brightness_red(self, steps=1):
        self.value[0] = self.value[0] - steps
        self.np[self.num] = self.value
        self.np.write()

    def pulse_led(self, steps_per_loop=1):
        if not self.decrease:
            self.increase_brightness_red(steps=steps_per_loop)
            if self.value[0] >= 255:
                self.decrease = True
        else:
            self.decrease_brightness_red(steps=steps_per_loop)
            if self.value[0] <= 0:
                self.decrease = False


def show_startup(np):
    for i in range(0,24):
        np[i] = (255, 255, 255)
        np.write()
        time.sleep(0.1)
        np[i] = (0, 0, 0)
        np.write()

def set_time():
    ntptime.settime()
    
    
def get_local_time():
    return time.localtime(time.time() + UTC_OFFSET)


def main():
    print("Start Device")
    
    logger = Logger()
    client = Client(logger)
    pin = Pin(MATRIX_PIN, Pin.OUT)
    np = NeoPixel(pin, 24)
    
    show_startup(np)
    client.activate()
    client.search_wlan()
    try:
        client.connect()
    except ConnectionError as e:
        logger.error(e)
        np[0] = (100, 0, 0)
        np[5] = (100, 0, 0)
        np[19] = (100, 0, 0)
        np[23] = (100, 0, 0)
        np.write()
        
    actual_time = get_local_time()
    logger.info("Received actual datetime: ", actual_time)
    logger.info("Date: ", actual_time[2], ".", actual_time[1], ".", actual_time[0])
    logger.info("Time: ", actual_time[3], ":", actual_time[4], ":", actual_time[5])

    animation_leds = [
        Led(randint(0, 23), np),
        Led(randint(0, 23), np),
        Led(randint(0, 23), np),
        Led(randint(0, 23), np),
        Led(randint(0, 23), np)
    ]

    while True:
        for i, led in enumerate(animation_leds):
            if led.value == [0, 0, 0]:
                led = Led(randint(0, 23), np)
                animation_leds[i] = led
        
        for led in animation_leds:
            led.pulse_led(steps_per_loop=randint(0, 1))

        time.sleep(0.005)
    

if __name__ == '__main__':
    main()