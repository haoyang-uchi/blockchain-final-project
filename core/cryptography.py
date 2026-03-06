# core/cryptography.py
from ecdsa.util import sigencode_der, sigdecode_der
import proto.energy_chain_pb2 as pb2
from ecdsa import SigningKey, VerifyingKey, SECP256k1
import hashlib


# generates a new SECP256k1 keypair
def generate_key():
    sk = SigningKey.generate(curve=SECP256k1)
    sk_hex = sk.to_string().hex()
    vk = sk.get_verifying_key()
    vk_hex = vk.to_string().hex()
    return sk_hex, vk_hex


# fetches the signing key and then signs the key
def sign_data(private_key_hex: str, data: bytes) -> bytes:
    sk = SigningKey.from_string(bytes.fromhex(private_key_hex), curve=SECP256k1)
    return sk.sign(data, hashfunc=hashlib.sha256, sigencode=sigencode_der)


# verifies teh signature given a bytes signature and data
def verify_signature(public_key_hex: str, signature: bytes, data: bytes) -> bool:
    try:
        vk = VerifyingKey.from_string(bytes.fromhex(public_key_hex), curve=SECP256k1)
        return vk.verify(
            signature, data, hashfunc=hashlib.sha256, sigdecode=sigdecode_der
        )
    except Exception as e:
        return False


# signs the payload of a transaction
def sign_tx(tx: pb2.Transaction, private_key_hex: str):
    if tx.HasField("grid_rate_tx"):
        tx.grid_rate_tx.signature = b""
        payload = tx.grid_rate_tx.SerializeToString()
        tx.grid_rate_tx.signature = sign_data(private_key_hex, payload)
    elif tx.HasField("order_tx"):
        tx.order_tx.signature = b""
        payload = tx.order_tx.SerializeToString()
        tx.order_tx.signature = sign_data(private_key_hex, payload)


# verifies that the transaction signature is using the sender's address
def verify_tx_signature(tx: pb2.Transaction) -> bool:
    if tx.HasField("grid_rate_tx"):
        pubkey = tx.grid_rate_tx.grid_address
        sig = tx.grid_rate_tx.signature

        # serialize without the signature to verify
        tx.grid_rate_tx.signature = b""
        payload = tx.grid_rate_tx.SerializeToString()
        tx.grid_rate_tx.signature = sig

        return verify_signature(pubkey, sig, payload)

    elif tx.HasField("order_tx"):
        pubkey = tx.order_tx.sender_address
        sig = tx.order_tx.signature

        tx.order_tx.signature = b""
        payload = tx.order_tx.SerializeToString()
        tx.order_tx.signature = sig

        return verify_signature(pubkey, sig, payload)

    # TradeTx doesn't have a user signature.
    return True
