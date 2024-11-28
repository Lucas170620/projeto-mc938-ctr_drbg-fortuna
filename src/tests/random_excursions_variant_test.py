import math
import time

from scipy.special import erfc
import pytest
import os
from src.algoritmos.CTR_DRBG import CTR_DRBG
from src.algoritmos.fortuna import FortunaGenerator, FortunaAccumulator
from src.utils.utils import generate_personalization_string


def bytes_to_bits(byte_data):
    return ''.join(f'{byte:08b}' for byte in byte_data)



def random_excursions_variant_test(bit_sequence:str):
    # Step 1: Convert binary sequence to -1 and +1
    X = [1 if bit == '1' else -1 for bit in bit_sequence]
    n = len(X)

    # Step 2: Calculate partial sums
    S = [0] * (n + 1)
    for i in range(1, n + 1):
        S[i] = S[i - 1] + X[i - 1]

    # Add zeros at the start and end as per step 3
    S_prime = [0] + S + [0]
    J = S_prime.count(0) - 1  # Count the number of zero crossings

    if J == 0:
        return False  # Insufficient zero crossings for valid random walk

    # Step 4: Calculate ξ_x for each state (-9 to +9)
    for x in range(-9, 10):
        if x == 0:
            continue
        count_x = sum(1 for i in range(1, len(S_prime)) if S_prime[i] == x)
        p_value = erfc(abs(count_x - J) / math.sqrt(2 * J * (4 * abs(x) - 2)))
        if p_value < 0.01:  # If any state fails, the sequence is not random
            return False

    # If all states pass, return True
    return True

num_executions = 10

@pytest.mark.parametrize("sample_size", [ 1048576, 2097152, 4194304 ])
@pytest.mark.rev
def test_fortuna_random_excursions_variant(sample_size):
    aes_key_size_bits = 256
    aes_key_size_bytes = aes_key_size_bits // 8
    for _ in range(num_executions):
        generator = FortunaGenerator(aes_key_size_bytes)
        accumulator = FortunaAccumulator()
        accumulator.add_random_event(1, os.urandom(32))  # Fonte 1
        accumulator.add_random_event(2, time.time_ns().to_bytes(8, 'big'))
        if accumulator.should_reseed():
            accumulator.reseed_generator(generator)
        bit_sequence = generator.generate(sample_size)
        bit_sequence = bytes_to_bits(bit_sequence)
        assert random_excursions_variant_test(bit_sequence)


@pytest.mark.parametrize("sample_size", [ 1048576, 2097152, 4194304 ])
@pytest.mark.rev
@pytest.mark.ctr_drbg
def test_ctr_drbg_random_excursions_variant(sample_size):
    aes_key_size_bits = 256
    for _ in range(num_executions):
        entropy_input = os.urandom(128)
        generator = CTR_DRBG(aes_bits=aes_key_size_bits)
        generator.instantiate(entropy_input,generate_personalization_string())
        generator.reseed(os.urandom(128),generate_personalization_string())
        bit_sequence = generator.generate(sample_size)
        bit_sequence = bytes_to_bits(bit_sequence)
        assert random_excursions_variant_test(bit_sequence)
