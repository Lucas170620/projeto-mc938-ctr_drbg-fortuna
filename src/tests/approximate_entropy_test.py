import time

import numpy as np
from scipy.special import gammaincc
import pytest
import os
from src.algoritmos.CTR_DRBG import CTR_DRBG
from src.algoritmos.fortuna import FortunaGenerator, FortunaAccumulator
from src.utils.utils import generate_personalization_string


def bytes_to_bits(byte_data):
    return ''.join(f'{byte:08b}' for byte in byte_data)

def phi(m, sequence, n):
    padded_sequence = sequence + sequence[:m - 1]
    counts = {}
    for i in range(n):
        block = tuple(padded_sequence[i:i + m])
        if block in counts:
            counts[block] += 1
        else:
            counts[block] = 1
    total_count = sum(counts.values())
    probabilities = [count / total_count for count in counts.values()]
    resultado = sum(p * np.log(p) for p in probabilities)
    return resultado


def approximate_entropy_test(sequence, m):
    n = len(sequence)
    ap_en = phi(m, sequence, n) - phi(m+1, sequence, n)
    chi_square = 2 * n * (np.log(2) - ap_en)
    p_value = float(gammaincc(2 ** (m - 1), chi_square / 2))
    return p_value

num_executions = 10

@pytest.mark.parametrize(
    "sample_size, m", [(128, 7), (512, 9), (2048, 11), (8192, 13), (32768, 15)]
)
@pytest.mark.aet
def test_fortuna_entropy(sample_size, m):
    aes_key_size_bits = 256
    aes_key_size_bytes = aes_key_size_bits // 8
    for _ in range(num_executions):
        generator = FortunaGenerator(aes_key_size_bytes)
        accumulator = FortunaAccumulator()
        accumulator.add_random_event(1, os.urandom(32))
        accumulator.add_random_event(2, time.time_ns().to_bytes(8, 'big'))
        if accumulator.should_reseed():
            accumulator.reseed_generator(generator)
        bit_sequence = generator.generate(sample_size)
        bit_sequence = [int(bit) for bit in bytes_to_bits(bit_sequence)]
        result = approximate_entropy_test(bit_sequence, m)
        assert result >= 0.01, (
            f"Fortuna Falhou usando AES-{aes_key_size_bits} "
            f"para n = {sample_size}, m = {m}, execução {_ + 1}"
        )




@pytest.mark.parametrize(
    "sample_size, m", [(128, 7), (512, 9), (2048, 11), (8192, 13), (32768, 15)]
)
@pytest.mark.aet
def test_ctr_drbg_entropy(sample_size, m):
    aes_key_size_bits = 256
    for _ in range(num_executions):
        entropy_input = os.urandom(516)
        generator = CTR_DRBG(aes_bits=aes_key_size_bits)
        generator.instantiate(entropy_input,generate_personalization_string())
        generator.reseed(os.urandom(516),generate_personalization_string())
        bit_sequence = generator.generate(sample_size)
        bit_sequence = [int(bit) for bit in bytes_to_bits(bit_sequence)]
        result = approximate_entropy_test(bit_sequence, m)
        assert result >= 0.01, (
            f"CTR_DRBG Falhou usando AES-{aes_key_size_bits} "
            f"para n = {sample_size}, m = {m}, execução {_ + 1}"
        )
