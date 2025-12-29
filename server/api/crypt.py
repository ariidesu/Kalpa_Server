import hashlib
import os
import hmac
import base64
import json
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from Crypto.Cipher import PKCS1_OAEP

def hash_password(password: str, salt: bytes = None) -> str:
    if salt is None:
        salt = os.urandom(16)
    pwd_hash = hashlib.pbkdf2_hmac(
        'sha512',
        password.encode('utf-8'),
        salt,
        100_000
    )
    return base64.b64encode(salt + pwd_hash).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    decoded = base64.b64decode(hashed.encode('utf-8'))
    salt = decoded[:16]
    stored_hash = decoded[16:]
    pwd_hash = hashlib.pbkdf2_hmac(
        'sha512',
        password.encode('utf-8'),
        salt,
        100_000
    )
    return hmac.compare_digest(pwd_hash, stored_hash)

async def play_decrypt(request_post):
    from api.templates_norm import PLAY_CRYPTOR
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