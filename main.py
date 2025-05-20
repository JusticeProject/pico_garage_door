import time
import random
import ucryptolib
from machine import Pin
from ble_uart_peripheral import BLE_UART

###############################################################################

newChallenge = b""
challengeSentTime = 0
# This is just one example AES key. To generate a new one that is not committed to GitHub repo then run testClient.py
preshared_key = b"\x07\x8b\xf07\x1b\x94\xbfz=\xfa&D\xa2\x07\x0e\x00\x81~\x83\x96\xe5.j\x19'\x9f\r?\xa9\xbb\x00h"

###############################################################################

def on_connection(addr):
    print("connection from", addr)
    random.seed(time.time())

###############################################################################

def on_disconnect(addr):
    print("disconnect from", addr)

###############################################################################

def encryptChallenge(plaintext):
    # ECB is not very secure in most applications since you can detect repeated patterns
    encrypter = ucryptolib.aes(preshared_key, 1)
    # must encrypt a block size modulo 16 bytes
    ciphertext = encrypter.encrypt(plaintext)
    return ciphertext

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

def decryptResponse(ciphertext):
    decrypter = ucryptolib.aes(preshared_key, 1)
    plaintext = decrypter.decrypt(ciphertext)
    return plaintext

###############################################################################

def createChallenge():
    challengeList = [random.randint(0, 255) for i in range(0, 128)]
    challenge = bytes(challengeList)
    return challenge

###############################################################################

def verifyChallenge(challenge, response):
    expected = manipulateBytes(challenge)
    decrypted = decryptResponse(response)

    if (expected == decrypted):
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
        ciphertext = encryptChallenge(newChallenge)
        uart.write(ciphertext)
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
uart = BLE_UART("pico_w")
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
