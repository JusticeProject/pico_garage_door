# pip install pycryptodome

from Crypto.Random import get_random_bytes

###############################################################################

# To generate a new key, note the output from the below functions.
# And don't commit it to GitHub!!
preshared_key = get_random_bytes(32) # key must be 32 bytes = 256 bits
print("New AES key generated:")

# print key for Python usage
print(preshared_key)

# print key for Dart usage
dartKey = "["
for i in range(0, len(preshared_key)):
    dartKey = dartKey + str(preshared_key[i]) + ","
dartKey += "]"
print(dartKey)

# plainText = b"Hello world"
# for i in range(0, 128-len(plainText)):
#     plainText += b" "
# print(f"{len(plainText)} bytes: {plainText}")

# cipherText = encryptToPicoW(plainText)
# print(f"{len(cipherText)} bytes: {cipherText}")

#decrypted = decryptFromPicoW(cipherText)
#print(f"{len(decrypted)} bytes: {decrypted}")

# fd = open("key.bin", "wb")
# fd.write(preshared_key)
# fd.close()

# fd = open("ciphertext.bin", "wb")
# fd.write(cipherText)
# fd.close()
