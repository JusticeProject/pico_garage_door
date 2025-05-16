# pip install pycryptodome
# pip install bleak

from bleak import BleakClient
import asyncio

from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

###############################################################################

# Note: they are reversed from ble_uart_peripheral.py
UART_TX_UUID = "6E400002-B5A3-F393-E0A9-E50E24DCCA9E"
UART_RX_UUID = "6E400003-B5A3-F393-E0A9-E50E24DCCA9E"
recvdData = b""

###############################################################################

def decryptFromPicoW(cipherText):
    return cipherText

###############################################################################

def manipulateBytes(byteData):
    return byteData

###############################################################################

def encryptToPicoW(plainText):
    return plainText

###############################################################################

def on_rx(sender, data):
    print("on_rx:")
    #print(sender)
    #print(data)
    print(len(data))
    global recvdData
    recvdData = data

###############################################################################

# if program crashes before disconnecting then run:
# bluetoothctl
# disconnect 2C:CF:67:D9:A4:59

async def run(address, loop):
    client = BleakClient(address, loop=loop)
    await client.connect()
    print(f"Connected: {client.is_connected}")

    await client.start_notify(UART_RX_UUID, on_rx)
    await asyncio.sleep(1)
    await client.write_gatt_char(UART_TX_UUID, b"Knock")

    global recvdData
    while True:
        if len(recvdData) > 0:
            plainText = decryptFromPicoW(recvdData)
            newPlainText = manipulateBytes(plainText)
            newCipherText = encryptToPicoW(newPlainText)
            await client.write_gatt_char(UART_TX_UUID, newCipherText)
            await asyncio.sleep(1)
            await client.disconnect()
            return
        else:
            await asyncio.sleep(1)

###############################################################################

address = ("2C:CF:67:D9:A4:59")
loop = asyncio.get_event_loop()
loop.run_until_complete(run(address, loop))

###############################################################################

# to generate a new key:
preshared_key = get_random_bytes(32) # key must be 32 bytes = 256 bits
print("New AES key generated:")
print(preshared_key)

# this is one example key that was generated
preshared_key = b"\x07\x8b\xf07\x1b\x94\xbfz=\xfa&D\xa2\x07\x0e\x00\x81~\x83\x96\xe5.j\x19'\x9f\r?\xa9\xbb\x00h"
encrypter = AES.new(preshared_key, AES.MODE_ECB)
plaintext = "Hello world!!!!!Hello world!!!!!Hello world!!!!!Hello world!!!!!" # must encrypt a block size modulo 16 bytes
print(len(plaintext))
ciphertext = encrypter.encrypt(plaintext.encode())
print(len(ciphertext))
print(ciphertext)


decrypter = AES.new(preshared_key, AES.MODE_ECB)
plaintext = decrypter.decrypt(ciphertext)
print(plaintext.decode())


# On the micropython side:
"""import ucryptolib
import binascii
preshared_key = b"\x07\x8b\xf07\x1b\x94\xbfz=\xfa&D\xa2\x07\x0e\x00\x81~\x83\x96\xe5.j\x19'\x9f\r?\xa9\xbb\x00h"
print(f"length of key = {len(preshared_key)}")
encrypter = ucryptolib.aes(preshared_key, 1) # ECB is not very secure in most applications since you can detect repeated patterns
ciphertext = encrypter.encrypt("Hello world!!!!!Hello world!!!!!Hello world!!!!!Hello world!!!!!".encode()) # must encrypt a block size modulo 16 bytes
cipertext_base64 = binascii.b2a_base64(ciphertext)
print(cipertext_base64)

decrypter = ucryptolib.aes(preshared_key, 1)
ciphertext = binascii.a2b_base64(cipertext_base64)
plaintext = decrypter.decrypt(ciphertext)
print(plaintext.decode())"""
