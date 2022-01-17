import base64
import json
# from Crypto.Cipher import AES

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend


class WXBizDataCrypt:
    def __init__(self, app_id, session_key):
        self.app_id = app_id
        self.session_key = session_key

    # def decrypt(self, encrypted_data, iv):
    #     # base64 decode
    #     session_key = base64.b64decode(self.session_key)
    #     encrypted_data = base64.b64decode(encrypted_data)
    #     iv = base64.b64decode(iv)
    #
    #     cipher = AES.new(session_key, AES.MODE_CBC, iv)
    #
    #     decrypted = json.loads(self._un_pad(cipher.decrypt(encrypted_data)))
    #flexible
    #     if decrypted['watermark']['appid'] != self.app_id:
    #         raise Exception('Invalid Buffer')
    #
    #     return decrypted

    def decrypt(self, encrypted_data, iv):
        # base64 decode
        # session_key = base64.b64decode(self.session_key)
        session_key = self.session_key
        encrypted_data = base64.b64decode(encrypted_data)
        iv = base64.b64decode(iv)


        backend = default_backend()
        cipher = Cipher(algorithms.AES(session_key), modes.CBC(iv), backend=backend)
        decrypt = cipher.decryptor()

        decrypted = json.loads(self._un_pad(decrypt.update(encrypted_data) + decrypt.finalize()))

        return decrypted

    @staticmethod
    def _un_pad(s):
        return s[:-ord(s[len(s) - 1:])]


if __name__ == '__main__':
    print('abcd')
    iv = 'qPtemrEaMiQgZ68O'
    c = WXBizDataCrypt('abcd', "4xkpBxT8cvZvWmrq")