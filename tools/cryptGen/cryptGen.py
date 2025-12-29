from Crypto.PublicKey import RSA
import base64

def to_rsa_key_value(pubkey):
    n = pubkey.n
    e = pubkey.e
    modulus_b64 = base64.b64encode(n.to_bytes((n.bit_length() + 7) // 8, 'big')).decode('ascii')
    exponent_b64 = base64.b64encode(e.to_bytes((e.bit_length() + 7) // 8, 'big')).decode('ascii')
    xml = f"<RSAKeyValue><Exponent>{exponent_b64}</Exponent><Modulus>{modulus_b64}</Modulus></RSAKeyValue>"
    return xml

key = RSA.generate(2048)
private_pem = key.export_key().decode()
public_xml = to_rsa_key_value(key.publickey())

with open("play_private.pem", "w") as private_file:
    private_file.write(private_pem)

with open("play_public.xml", "w") as public_file:
    public_file.write(public_xml)

print("Keys have been saved to 'play_private.pem' and 'play_public.xml'.")