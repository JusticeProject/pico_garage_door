# pip install pycryptodome

from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import binascii

# to generate a new key:
#preshared_key = get_random_bytes(32) # key must be 32 bytes
#print(preshared_key)

# this is one example key that was generated
preshared_key = b"\x07\x8b\xf07\x1b\x94\xbfz=\xfa&D\xa2\x07\x0e\x00\x81~\x83\x96\xe5.j\x19'\x9f\r?\xa9\xbb\x00h"
encrypter = AES.new(preshared_key, AES.MODE_ECB)
plaintext = "Hello world!!!!!Hello world!!!!!Hello world!!!!!Hello world!!!!!" # must encrypt a block size modulo 16 bytes
print(len(plaintext))
ciphertext = encrypter.encrypt(plaintext.encode())
print(len(ciphertext))
ciphertext_base64 = binascii.b2a_base64(ciphertext)
print(len(ciphertext_base64))
print(ciphertext_base64)

# this is the encrypted result in base64
# b'vjEXib4g3H9EEzqc6/StRL4xF4m+INx/RBM6nOv0rUS+MReJviDcf0QTOpzr9K1EvjEXib4g3H9EEzqc6/StRA==\n'

decrypter = AES.new(preshared_key, AES.MODE_ECB)
ciphertext = binascii.a2b_base64(ciphertext_base64)
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
