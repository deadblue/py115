__author__ = 'deadblue'

import secrets


class Cipher():

    def __init__(self, n: bytes, e: int) -> None:
        self._n = int.from_bytes(n, 'big')
        self._e = e
        self._key_len = len(n)


    def _encrypt_slice(self, segment: bytes) -> bytes:
        # Make pad
        pad_size = self._key_len - len(segment)
        pad_buf = bytearray(pad_size)
        pad_buf[0], pad_buf[1] = 0, 2
        for i in range(pad_size - 3):
            pad_buf[2 + i] = secrets.randbelow(0xff) + 1
        pad_buf[-1] = 0
        msg = int.from_bytes(pad_buf + segment, 'big')
        return pow(msg, self._e, self._n).to_bytes(self._key_len, 'big')


    def encrypt(self, plaintext: bytes) -> bytes:
        ciphertext = bytearray()
        remain_size = len(plaintext)
        while remain_size > 0:
            slice_size = self._key_len - 11
            if slice_size > remain_size:
                slice_size = remain_size
            ciphertext.extend(
                self._encrypt_slice(plaintext[:slice_size])
            )
            plaintext = plaintext[slice_size:]
            remain_size -= slice_size
        return bytes(ciphertext)


    def _decrypt_slice(self, segment: bytes) -> bytes:
        msg = int.from_bytes(segment, 'big')
        ret = pow(msg, self._e, self._n).to_bytes(self._key_len, 'big')
        for i, b in enumerate(ret):
            if i != 0 and b == 0:
                ret = ret[i+1:]
                break
        return ret


    def decrypt(self, ciphertext: bytes) -> bytearray:
        plaintext = bytearray()
        remain_size = len(ciphertext)
        while remain_size > 0:
            slice_size = self._key_len
            if slice_size > remain_size:
                slice_size = remain_size
            plaintext.extend(
                self._decrypt_slice(ciphertext[:slice_size])
            )
            ciphertext = ciphertext[slice_size:]
            remain_size -= slice_size
        return plaintext
