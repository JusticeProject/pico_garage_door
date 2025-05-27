import socket
from Crypto.Cipher import AES

###############################################################################

# a sample shared key
preshared_key = b"\x07\x8b\xf07\x1b\x94\xbfz=\xfa&D\xa2\x07\x0e\x00\x81~\x83\x96\xe5.j\x19'\x9f\r?\xa9\xbb\x00h"

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

server_addr_port = socket.getaddrinfo("picow.local", 17812)[0][-1]
print(server_addr_port)

# Set up UDP client
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
 
# Send request to the server
client_socket.sendto(b"KnockKnock", server_addr_port)

# Receive data from the server
cipherText, addr = client_socket.recvfrom(1024)
plainText = decryptFromPicoW(cipherText)
newPlainText = manipulateBytes(plainText)
newCipherText = encryptToPicoW(newPlainText)
client_socket.sendto(newCipherText, server_addr_port)
