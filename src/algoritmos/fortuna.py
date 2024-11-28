import os
import hashlib
from Crypto.Cipher import AES

class FortunaGenerator:
    def __init__(self, keylen):
        self.key = bytes([0] * keylen)
        self.counter = int.from_bytes(os.urandom(16), 'little')

    def _increment_counter(self):
        self.counter = (self.counter + 1) % (1 << 128)

    def _encrypt_block(self):
        cipher = AES.new(self.key, AES.MODE_ECB)
        block = self.counter.to_bytes(16, 'little')
        self._increment_counter()
        return cipher.encrypt(block)

    def reseed(self, seed):
        hasher = hashlib.sha256()
        hasher.update(self.key + seed)
        self.key = hasher.digest()
        self.counter = 0

    def generate(self, n_bits):
        n_bytes = (n_bits + 7) // 8
        if n_bytes > (1 << 20):
            raise ValueError("Request too large")
        output = b''
        while len(output) < n_bytes:
            output += self._encrypt_block()
        return output[:n_bytes]

class FortunaAccumulator:
    def __init__(self):
        self.pools = [hashlib.sha256() for _ in range(32)]
        self.pool_index = 0
        self.reseed_counter = 0

    def add_random_event(self, source_number, event_data):
        pool_number = self.pool_index % 32
        self.pools[pool_number].update(bytes([source_number]) + len(event_data).to_bytes(1, 'big') + event_data)
        self.pool_index = (self.pool_index + 1) % 32

    def should_reseed(self):
        return self.pools[0].digest_size > 32

    def reseed_generator(self, generator):
        if self.should_reseed():
            seed_material = b''
            for i in range(32):
                if (1 << i) & self.reseed_counter:
                    seed_material += self.pools[i].digest()
                    self.pools[i] = hashlib.sha256()
            generator.reseed(seed_material)
            self.reseed_counter += 1


