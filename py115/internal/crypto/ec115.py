__author__ = 'deadblue'

import binascii
import logging
import random
import struct

from Crypto.Cipher import AES
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
import lz4.block

_server_pub_key = bytes([
    0x04, 0x57, 0xa2, 0x92, 0x57, 0xcd, 0x23, 0x20, 
    0xe5, 0xd6, 0xd1, 0x43, 0x32, 0x2f, 0xa4, 0xbb, 
    0x8a, 0x3c, 0xf9, 0xd3, 0xcc, 0x62, 0x3e, 0xf5, 
    0xed, 0xac, 0x62, 0xb7, 0x67, 0x8a, 0x89, 0xc9, 
    0x1a, 0x83, 0xba, 0x80, 0x0d, 0x61, 0x29, 0xf5, 
    0x22, 0xd0, 0x34, 0xc8, 0x95, 0xdd, 0x24, 0x65, 
    0x24, 0x3a, 0xdd, 0xc2, 0x50, 0x95, 0x3b, 0xee, 
    0xba,
])

_crc_salt = b'^j>WD3Kr?J2gLFjD4W2y@'

_logger = logging.getLogger(__name__)

class Cipher:

    def __init__(self) -> None:
        # Use P-224 curve
        curve = ec.SECP224R1()
        # Parse server key
        server_key = ec.EllipticCurvePublicKey.from_encoded_point(
            curve=curve, data=_server_pub_key)
        # Generate client key
        ec_key = ec.generate_private_key(
            curve=curve, backend=default_backend())
        self._pub_key = b'\x1d' + ec_key.public_key().public_bytes(
            encoding=Encoding.X962, format=PublicFormat.CompressedPoint)
        # ECDH key exchange
        shared_secret = ec_key.exchange(ec.ECDH(), server_key)
        self._aes_key = shared_secret[:16]
        self._aes_iv = shared_secret[-16:]
    
    def encode_token(self, timestamp: int) -> str:
        token = bytearray(struct.pack(
            '<15sBII15sBI',
            self._pub_key[:15], 0, 115, timestamp,
            self._pub_key[15:], 0, 1
        ))
        r1, r2 = random.randint(0, 0xff), random.randint(0, 0xff)
        for i in range(len(token)):
            if i < 24:
                token[i] = token[i] ^ r1
            else:
                token[i] = token[i] ^ r2
        # Calculate and append CRC32 checksum
        checksum = binascii.crc32(_crc_salt + token) & 0xffffffff
        token += struct.pack('<I', checksum)
        # Base64 encode
        return binascii.b2a_base64(token, newline=False).decode()

    def encode(self, data: bytes) -> bytes:
        pad_size = AES.block_size - len(data) % AES.block_size
        if pad_size != AES.block_size:
            data += bytes([0] * pad_size)
        encrypter = AES.new(
            key=self._aes_key,
            mode=AES.MODE_CBC,
            iv=self._aes_iv
        )
        return encrypter.encrypt(data)

    def decode(self, data: bytes) -> bytes:
        ciphertext, tail = data[:-12], bytearray(data[-12:])
        # Decrypt
        decrypter = AES.new(
            key = self._aes_key, 
            mode = AES.MODE_CBC, 
            iv = self._aes_iv
        )
        plaintext = decrypter.decrypt(ciphertext)
        # Get uncompress size
        for i in range(4):
            tail[i] = tail[i] ^ tail[7]
        dst_size, = struct.unpack('<I', tail[:4])
        # Decompress
        buf = []
        while dst_size > 0:
            uncompressed_size = dst_size
            if uncompressed_size > 8192:
                uncompressed_size = 8192
            src_size, = struct.unpack('<H', plaintext[:2])
            buf.append(lz4.block.decompress(
                plaintext[2:src_size+2], uncompressed_size
            ))
            # Move to next block
            plaintext = plaintext[src_size+2:]
            dst_size -= uncompressed_size
        return buf[0] if len(buf) == 0 else b''.join(buf)
