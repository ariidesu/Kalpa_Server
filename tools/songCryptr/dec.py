import base64
import json
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from Crypto.Cipher import PKCS1_OAEP
import os
from Crypto.PublicKey import RSA

with open(os.path.join('play_private.pem'), 'r', encoding='utf-8') as f:
    private_key = f.read()
    PLAY_CRYPTOR = RSA.import_key(private_key)

def play_decrypt(request_post):
    user_play_data = request_post.get('userPlayData')
    key_b64 = request_post.get('encryptedKey')
    iv_b64 = request_post.get('encryptedIV')

    if not user_play_data or not key_b64 or not iv_b64:
        return None

    encrypted_key = base64.b64decode(key_b64)
    encrypted_iv = base64.b64decode(iv_b64)
    encrypted_data = base64.b64decode(user_play_data)

    rsa_cipher = PKCS1_OAEP.new(PLAY_CRYPTOR)
    aes_key = rsa_cipher.decrypt(encrypted_key)
    aes_iv = rsa_cipher.decrypt(encrypted_iv)

    aes_cipher = AES.new(aes_key, AES.MODE_CBC, aes_iv)
    decrypted_data = unpad(aes_cipher.decrypt(encrypted_data), AES.block_size)

    play_json = json.loads(decrypted_data.decode())

    return play_json

play_data = ""
encrypted_key = ''
encrypted_iv = ''

def main():
    request_post = {
        'userPlayData': play_data,
        'encryptedKey': encrypted_key,
        'encryptedIV': encrypted_iv
    }
    play_json = play_decrypt(request_post)
    print(json.dumps(play_json, indent=4))

if __name__ == "__main__":
    main()