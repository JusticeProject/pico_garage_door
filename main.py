import time
import random
from machine import Pin
from ble_uart_peripheral import BLE_UART

###############################################################################

newChallenge = b""
challengeSentTime = 0

###############################################################################

def on_connection(addr):
    print("connection from", addr)
    random.seed(time.time())

###############################################################################

def on_disconnect(addr):
    print("disconnect from", addr)

###############################################################################

def manipulateBytes(data):
    newData = []
    for i in range(0, len(data)):
        newByte = data[i] + i + 1
        if (newByte > 255):
            newByte -= 255
        newData.append(newByte)
    return bytes(newData)

###############################################################################

def createChallenge():
    challengeList = [random.randint(0, 255) for i in range(0, 128)]
    challenge = bytes(challengeList)
    return challenge

###############################################################################

def verifyChallenge(challenge, response):
    expected = manipulateBytes(challenge)

    if (expected == response):
        return True
    else:
        return False

###############################################################################

def on_rx():
    global newChallenge
    global challengeSentTime

    data = uart.read()
    print(len(data))

    # if len is 5 then it's probably a request for a challenge, else check if it's the right block size for our AES data
    if (len(data) == 5) and (data == b"Knock"):
        newChallenge = createChallenge()
        uart.write(newChallenge)
        challengeSentTime = time.time()
        led.off()
    elif (len(data) == 128):
        verified = verifyChallenge(newChallenge, data)
        if verified:
            led.on()
            newChallenge = b""
        else:
            print("Challenge failed")
            led.off()
    else:
        print("Unknown data")
        led.off()

###############################################################################

led = Pin("LED", Pin.OUT)
led.off()
print("Creating bluetooth device...")
uart = BLE_UART("picow")
uart.set_connect_callback(on_connection)
uart.set_disconnect_callback(on_disconnect)
uart.set_rx_callback(on_rx)
print("...done")

###############################################################################

try:
    while True:
        now = time.time()
        
        # check if we timed out
        if (len(newChallenge) > 0) and (now - challengeSentTime > 20):
            print("Challenge timed out")
            newChallenge = b""
        #uart.write(bytes((1,2,3,4)))
        time.sleep_ms(1000)
except KeyboardInterrupt:
    pass

uart.close()
