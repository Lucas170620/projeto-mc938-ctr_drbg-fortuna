import time

import pytest
import numpy as np
import os

from scipy.special import erfc

from src.algoritmos.CTR_DRBG import CTR_DRBG
from src.algoritmos.fortuna import FortunaGenerator, FortunaAccumulator
from src.utils.utils import generate_personalization_string

num_executions = 10
aes_key_size_bits = 256



def bytes_to_bits(byte_data):
    return ''.join(f'{byte:08b}' for byte in byte_data)

def DFT(X):
    return np.fft.fft(X)

def discrete_fourier_transform_test(bits):
    n , x = len(bits) , np.array([(2 * int(bit)) - 1 for bit in bits])
    S = DFT(x)
    S_linha = S[:n // 2]
    M , T = np.abs(S_linha) , np.sqrt(np.log(1 / 0.05) * n)
    N0 , N1 = 0.95 * n / 2 , np.sum(M < T)
    d = (N1 - N0) / np.sqrt( n * 0.95 * 0.05 / 4)
    p_value = erfc(np.abs(d) / np.sqrt(2))
    return p_value



@pytest.mark.parametrize("sample_size",[ 1024,2048,4096,8192, 32768])
@pytest.mark.dft
def test_fortuna_dft_reseed(sample_size):
    aes_key_size_bytes =  aes_key_size_bits // 8
    for _ in range(num_executions):
        generator = FortunaGenerator(aes_key_size_bytes)
        accumulator = FortunaAccumulator()
        accumulator.add_random_event(1, os.urandom(32))  # Fonte 1
        accumulator.add_random_event(2, time.time_ns().to_bytes(8, 'big'))  # Fonte 2
        if accumulator.should_reseed():
            accumulator.reseed_generator(generator)
        bit_sequence = generator.generate(sample_size)
        bit_sequence = bytes_to_bits(bit_sequence)
        result = discrete_fourier_transform_test(bit_sequence)
        assert result

@pytest.mark.parametrize("sample_size",[ 1024,2048,4096,8192, 32768])
@pytest.mark.dft
def test_ctr_drbg_dft_reseed(sample_size):
    for _ in range(num_executions):
        entropy_input = os.urandom(48)
        generator = CTR_DRBG(aes_bits=aes_key_size_bits)
        generator.instantiate(entropy_input,generate_personalization_string())
        bit_sequence = generator.generate(sample_size)
        bit_sequence = bytes_to_bits(bit_sequence)
        result = discrete_fourier_transform_test(bit_sequence)
        assert result
