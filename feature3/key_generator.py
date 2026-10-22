from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from Crypto.Cipher import _mode_eax
from Crypto.Random import get_random_bytes
import base64

key = get_random_bytes(32)
IV = get_random_bytes(16)

with open("keyIV.txt", "wb") as file:
    file.write(key)
    file.write(IV)






    