import time
from machine import Pin
from neopixel import NeoPixel
import ntptime

from logging import Logger
from networking import Client
from networking import ConnectionError


MATRIX_PIN = 32
UTC_OFFSET = 0 * 60 * 60

class APnotFound(Exception):
    """Raises when the Router have found no AP"""

def show_startup(np):
    for i in range(0,24):
        np[i] = (50, 50, 50)
        np.write()
        time.sleep(0.05)
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
    

if __name__ == '__main__':
    main()