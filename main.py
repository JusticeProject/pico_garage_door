import time
import random
from machine import Pin
from ble_uart_peripheral import BLE_UART

###############################################################################

newChallenge = ""
challengeSentTime = 0

###############################################################################

def on_connection(addr):
    print("connection from", addr)
    random.seed(time.time())

###############################################################################

def on_rx():
    global newChallenge
    global challengeSentTime

    print("rx:")
    data = uart.read()
    print(data)
    print(len(data))
    #for val in data:
    #    print(val)
    # if len is 5 then it's probably a request for a challenge, else check if it's the right block size for AES
    try:
        data_str = data.decode()
        print(data_str)
        if (data_str == "Hello"):
            newChallenge = "decode this"
            uart.write(newChallenge)
            challengeSentTime = time.time()
            led.off()
        elif (data_str == "world"):
            led.on()
            newChallenge = ""
    except UnicodeError as e:
        print("could not decode")
        led.off()

###############################################################################

led = Pin("LED", Pin.OUT)
led.off()
print("Creating bluetooth device...")
uart = BLE_UART("picow")
uart.set_connect_callback(on_connection)
uart.set_rx_callback(on_rx)
print("...done")

###############################################################################

try:
    while True:
        now = time.time()
        
        # check if we timed out
        if (now - challengeSentTime > 20):
            newChallenge = ""
        #uart.write(bytes((1,2,3,4)))
        time.sleep_ms(1000)
except KeyboardInterrupt:
    pass

uart.close()
