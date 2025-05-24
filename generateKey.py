# pip install pycryptodome

from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

###############################################################################

# To generate a new key, note the output from the below functions.
# And don't commit it to GitHub!!
preshared_key = get_random_bytes(32) # key must be 32 bytes = 256 bits
print("New AES key generated:")

# a sample shared key
#preshared_key = b"\x07\x8b\xf07\x1b\x94\xbfz=\xfa&D\xa2\x07\x0e\x00\x81~\x83\x96\xe5.j\x19'\x9f\r?\xa9\xbb\x00h"

# print key for Python usage
print(preshared_key)

# print key for Dart usage
dartKey = "["
for i in range(0, len(preshared_key)):
    dartKey = dartKey + str(preshared_key[i]) + ","
dartKey += "]"
print(dartKey)

###############################################################################

def decryptFromPicoW(cipherText):
    decrypter = AES.new(preshared_key, AES.MODE_ECB)
    plainText = decrypter.decrypt(cipherText)
    return plainText

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

def encryptToPicoW(plainText):
    encrypter = AES.new(preshared_key, AES.MODE_ECB)
    cipherText = encrypter.encrypt(plainText)
    return cipherText

###############################################################################

plainText = b"Hello world"
for i in range(0, 128-len(plainText)):
    plainText += b" "
print(f"{len(plainText)} bytes: {plainText}")

cipherText = encryptToPicoW(plainText)
print(f"{len(cipherText)} bytes: {cipherText}")

#decrypted = decryptFromPicoW(cipherText)
#print(f"{len(decrypted)} bytes: {decrypted}")

fd = open("key.bin", "wb")
fd.write(preshared_key)
fd.close()

fd = open("ciphertext.bin", "wb")
fd.write(cipherText)
fd.close()
