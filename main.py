from machine import Pin
import network
import usocket as socket
import secrets
import time
import random
import ucryptolib

# from https://toptechboy.com/sending-data-over-wifi-between-raspberry-pi-pico-w-and-your-pc/

###############################################################################

OPTOCOUPLER_GPIO_PIN = 0

# This is just one example AES key. To generate a new one that is not committed to GitHub repo then run generateKey.py
preshared_key = b"\x07\x8b\xf07\x1b\x94\xbfz=\xfa&D\xa2\x07\x0e\x00\x81~\x83\x96\xe5.j\x19'\x9f\r?\xa9\xbb\x00h"

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

def flashLED(led : Pin, count : int):
    for i in range(0, count):
        led.on()
        time.sleep_ms(250)
        led.off()
        time.sleep_ms(250)

###############################################################################

# status LED that's on the PicoW board
led = Pin("LED", Pin.OUT)
led.on()

# optocoupler - on will trigger the garage door
opto = Pin(OPTOCOUPLER_GPIO_PIN, Pin.OUT)
opto.off()

###############################################################################

time.sleep(1)
network.country("US") # or import rp2  then rp2.country("US")
network.hostname("picow")
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(secrets.SSID, secrets.PASSWORD)
 
# Wait for connection
while not wlan.isconnected():
    flashLED(led, 1)
    time.sleep(1)   
#print(wlan.ifconfig())

###############################################################################

# Set up UDP server
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind((wlan.ifconfig()[0], 17812))
#print(wlan.ifconfig()[0])

flashLED(led, 4)
led.off()
random.seed(time.time())

###############################################################################

newChallenge = b""
challengeSentTime = 0

try:
    while True:
        #print('Waiting for a request from the client...')
        data, client_address = server_socket.recvfrom(1024)
        #print(len(data))

        # check if we timed out
        now = time.time()
        if (len(newChallenge) > 0) and (now - challengeSentTime > 20):
            #print("Challenge timed out")
            newChallenge = b""
        
        # if len is 10 then it's probably a request for a challenge, else check if it's the right block size for our AES data
        if (len(data) == 10) and (data == b"KnockKnock"):
            newChallenge = createChallenge()
            ciphertext = encryptChallenge(newChallenge)
            server_socket.sendto(ciphertext, client_address)
            challengeSentTime = time.time()
        elif (len(data) == 128):
            verified = verifyChallenge(newChallenge, data)
            if verified:
                opto.on()
                time.sleep(1)
                opto.off()
                flashLED(led, 1)
                newChallenge = b""
            else:
                # challenge failed
                flashLED(led, 2)
        else:
            # unknown data
            flashLED(led, 3)

except KeyboardInterrupt:
    wlan.disconnect()
