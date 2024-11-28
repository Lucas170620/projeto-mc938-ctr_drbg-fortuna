from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from os import urandom

from src.utils.utils import xor, padding

aes_configs = {
        128: {"keylen": 16, "blocklen": 16, "ctr_len": 4, "reseed_interval": 2**48},
        192: {"keylen": 24, "blocklen": 16, "ctr_len": 4, "reseed_interval": 2**48},
        256: {"keylen": 32, "blocklen": 16, "ctr_len": 4, "reseed_interval": 2**48},
}


class CTR_DRBG:
    def __init__(self, aes_bits=256):
        if aes_bits not in aes_configs:
            raise ValueError("AES inválido. Escolha entre 128, 192 ou 256 bits.")
        config = aes_configs[aes_bits]
        self.keylen = config["keylen"]
        self.blocklen = config["blocklen"]
        self.ctr_len = config["ctr_len"]
        self.reseed_interval = config["reseed_interval"]
        self.seed_len = self.keylen + self.blocklen
        self.V = b"\x00" * self.blocklen
        self.Key = b"\x00" * self.keylen
        self.reseed_counter = 1

    def _block_encrypt(self, key, data):
        """Função de cifração de bloco com AES no modo ECB"""
        cipher = Cipher(algorithms.AES(key), modes.CTR(self.V), backend=default_backend())
        encryptor = cipher.encryptor()
        return encryptor.update(data) + encryptor.finalize()

    def _increment_counter(self, V):
        if self.ctr_len < self.blocklen:
            right = V[-self.ctr_len:]
            rightmost_bits = int.from_bytes(right, byteorder="big")
            rightmost_bits = (rightmost_bits + 1) % (2 ** (self.ctr_len * 8))
            leftmost_bits = V[:-self.ctr_len]
            rightmost_bits = rightmost_bits.to_bytes(self.ctr_len, byteorder="big")
            V = leftmost_bits + rightmost_bits
        else:
            V_as_int = int.from_bytes(V, byteorder="big")
            V_as_int = (V_as_int + 1) % (2 ** (self.blocklen * 8))
            V = V_as_int.to_bytes(self.blocklen, byteorder="big")
        return V

    def update(self, provided_data):
        temp = b""
        while len(temp) < self.seed_len:
            self.V = self._increment_counter(self.V)
            temp += self._block_encrypt(self.Key, self.V)

        temp = temp[: self.seed_len]
        temp = xor(temp, provided_data)
        self.Key = temp[:self.keylen]
        self.V = temp[self.keylen : self.seed_len]


    def instantiate(self, entropy_input, personalization_string=b""):
        personalization_string = padding(personalization_string[: self.seed_len],self.seed_len)
        entropy_input = entropy_input[:self.seed_len]
        seed_material = xor(entropy_input,personalization_string)
        self.update(seed_material)
        self.reseed_counter = 1

    def reseed(self, entropy_input, additional_input=b""):
        entropy_input = entropy_input[: self.seed_len]
        additional_input = padding(additional_input[:self.seed_len],self.seed_len)
        seed_material = xor(entropy_input,additional_input)
        self.update(seed_material)
        self.reseed_counter = 1

    def generate(self, requested_number_of_bits, additional_input=b""):
        if self.reseed_counter > self.reseed_interval:
            raise Exception("Reseed é necessário")
        if additional_input:
            additional_input = padding(additional_input,self.seed_len)
            self.update(additional_input)
        temp = b""
        while len(temp) < (requested_number_of_bits // 8):
            self.V = self._increment_counter(self.V)
            temp += self._block_encrypt(self.Key, self.V)
        returned_bits = temp[: requested_number_of_bits // 8]
        self.update(padding(additional_input,self.seed_len))
        self.reseed_counter += 1
        return returned_bits
