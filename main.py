import time
from machine import Pin
from neopixel import NeoPixel
import ntptime
from random import randint

from logging import Logger
from networking import Client
from networking import ConnectionError


MATRIX_PIN = 32
UTC_OFFSET = 1 * 60 * 60
DAY_SIMULATION = False

CALENDAR_LIST = [
    6,      # day 1 (0)
    12,     # day 2 (1)
    15,     # day 3 (2)
    8,      # day 4 (3)
    19,     # day 5 (4)  
    0,      # day 6 (5)
    22,     # day 7 (6)
    2,      # day 8 (7)
    7,      # day 9 (8)
    18,     # day 10 (9)
    11,     # day 11 (10)
    14,     # day 12 (11)
    4,      # day 13 (12)
    13,     # day 14 (13)
    17,     # day 15 (14)
    5,      # day 16 (15)
    20,     # day 17 (16)
    3,      # day 18 (17)
    21,     # day 19 (18)
    10,     # day 20 (19)
    9,      # day 21 (20)
    16,     # day 22 (21)
    1,      # day 23 (22)
    23      # day 24 (23)
]


class Led():
    def __init__(self, num, np):
        self.np = np
        self.num = num
        self.value = [0, 0, 0]
        self.decrease = False

    def set_color(self, color=[20, 20, 20]):
        self.value = color
        self.np[self.num] = self.value
        # self.np.write()

    def increase_brightness_red(self, steps=1):
        self.value[0] = self.value[0] + steps
        self.np[self.num] = self.value
        # self.np.write()

    def decrease_brightness_red(self, steps=1):
        self.value[0] = self.value[0] - steps
        self.np[self.num] = self.value
        # self.np.write()

    def pulse_led(self, steps_per_loop=1):
        if not self.decrease:
            self.increase_brightness_red(steps=steps_per_loop)
            if self.value[0] >= 255:
                self.decrease = True
        else:
            self.decrease_brightness_red(steps=steps_per_loop)
            if self.value[0] <= 0:
                self.decrease = False


class Timer():
    def __init__(self, timer_duration):
        self.start_millis = 0
        self.timer_duration = timer_duration

    def start(self):
        self.start_millis = time.ticks_ms()
    
    def restart(self):
        self.start_millis = time.ticks_ms()

    def get_duration(self):
        return self.timer_duration
    
    def check_time_over(self):
        if(time.ticks_ms() - self.start_millis >= self.timer_duration):
            return True
        else:
            return False


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
        
    ntptime.settime()
    actual_utc_time = time.localtime()
    logger.info("Received actual datetime: ", actual_utc_time)
    actual_time = get_local_time()
    logger.info("Datetime for german timezone: ", actual_time)
    logger.info("Date: ", actual_time[2], ".", actual_time[1], ".", actual_time[0])
    logger.info("Time: ", actual_time[3], ":", actual_time[4], ":", actual_time[5])

    animation_leds = [
        Led(randint(0, 23), np),
        Led(randint(0, 23), np),
        Led(randint(0, 23), np),
        Led(randint(0, 23), np),
        Led(randint(0, 23), np)
    ]

    more_animation_leds = [
        Led(randint(0, 23), np),
        Led(randint(0, 23), np),
        Led(randint(0, 23), np),
        Led(randint(0, 23), np),
        Led(randint(0, 23), np),
        Led(randint(0, 23), np),
        Led(randint(0, 23), np),
        Led(randint(0, 23), np),
        Led(randint(0, 23), np),
        Led(randint(0, 23), np)
    ]

    simulation_timer = Timer(2000)
    simulation_timer.start()

    day = actual_time[2]
    logger.info("actual day: ", day)

    while True:
        if not DAY_SIMULATION:
            day = actual_time[2]

        if simulation_timer.check_time_over() and DAY_SIMULATION:
            simulation_timer.restart()
            day = day + 1
            if day > 30:
                day = 1
            logger.info("Simulate Day: ", day)

        if day > 24:
            for i, led in enumerate(more_animation_leds):
                if led.value == [0, 0, 0]:
                    led = Led(randint(0, 23), np)
                    more_animation_leds[i] = led
            for led in more_animation_leds:
                led.pulse_led(steps_per_loop=randint(0, 1))

            np.write()
            time.sleep(0.005)
        else:
            # past days
            for past_day in range(1, day):
                past_day_led  = Led(CALENDAR_LIST[past_day-1], np)
                past_day_led.set_color([0, 20, 0])

            # animation leds
            for i, led in enumerate(animation_leds):
                if led.value == [0, 0, 0]:
                    led = Led(randint(0, 23), np)
                    animation_leds[i] = led
            for led in animation_leds:
                led.pulse_led(steps_per_loop=randint(0, 1))

            # actual day led
            led_num = CALENDAR_LIST[day-1]
            day_led = Led(led_num, np)
            day_led.set_color([255, 255, 255])

            np.write()
            time.sleep(0.005)
    

if __name__ == '__main__':
    main()