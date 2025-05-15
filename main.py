import time
from machine import Pin
from ble_uart_peripheral import BLE_UART

###############################################################################

led = Pin("LED", Pin.OUT)
led.on()
print("Creating bluetooth device...")
uart = BLE_UART("mpy-uart")
print("...done")

###############################################################################

newChallenge = ""
challengeSentTime = 0

def on_rx():
    global newChallenge
    global challengeSentTime
    print("rx:")
    data = uart.read()
    print(data)
    print(len(data))
    try:
        data_str = data.decode()
        print(data_str)
        if (data_str == "Hello"):
            newChallenge = "decode this"
            challengeSentTime = time.time()
            led.off()
        elif (data_str == "world"):
            led.on()
            newChallenge = ""
    except UnicodeError as e:
        print("could not decode")
        led.off()

uart.set_rx_callback(handler=on_rx)

try:
    while True:
        now = time.time()
        
        # check if we timed out
        if (now - challengeSentTime > 20):
            newChallenge = ""
        elif (len(newChallenge) > 0):
            uart.write(newChallenge)
        time.sleep_ms(1000)
except KeyboardInterrupt:
    pass

uart.close()
