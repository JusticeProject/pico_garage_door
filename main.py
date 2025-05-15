import time
from machine import Pin
from ble_uart_peripheral import BLE_UART

###############################################################################

newChallenge = ""
challengeSentTime = 0

###############################################################################

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
uart = BLE_UART("mpy-uart")
uart.set_rx_callback(handler=on_rx)
print("...done")

###############################################################################

try:
    while True:
        now = time.time()
        
        # check if we timed out
        if (now - challengeSentTime > 20):
            newChallenge = ""
        time.sleep_ms(1000)
except KeyboardInterrupt:
    pass

uart.close()
