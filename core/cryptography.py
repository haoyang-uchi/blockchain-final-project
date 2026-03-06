# core/cryptography.py
from ecdsa import SigningKey, VerifyingKey, SECP256k1

# generates a new SECP256k1 keypair
def generate_key():
    sk = SigningKey.generate(curve=SECP256k1)
    sk_hex = sk.to_string().hex()
    vk = sk.get_verifying_key()
    vk_hex = vk.to_string().hex()
    return sk_hex, vk_hex

