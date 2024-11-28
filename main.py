import os
import time
import matplotlib.pyplot as plt
from src.algoritmos.CTR_DRBG import CTR_DRBG
from src.algoritmos.fortuna import FortunaGenerator, FortunaAccumulator
from src.utils.utils import generate_personalization_string

def bytes_to_bits(byte_data):
    """
    Converte bytes em uma sequência de bits.
    """
    return ''.join(f'{byte:08b}' for byte in byte_data)

def calculate_block_probabilities(bit_sequence, block_size):
    """
    Calcula as probabilidades de ocorrência de padrões para blocos de tamanho block_size.
    """
    n = len(bit_sequence)
    # Estende a sequência para incluir os primeiros bits no final
    extended_sequence = bit_sequence + bit_sequence[:block_size - 1]
    # Gera padrões de blocos de tamanho block_size
    patterns = [''.join(extended_sequence[i:i + block_size]) for i in range(n)]
    # Conta a frequência de cada padrão
    pattern_counts = {pattern: patterns.count(pattern) for pattern in set(patterns)}
    # Calcula as probabilidades
    probabilities = {pattern: count / n for pattern, count in pattern_counts.items()}
    return probabilities

def plot_histogram(probabilities, title):
    """
    Plota um histograma das probabilidades de ocorrência dos padrões.
    """
    patterns, probs = zip(*sorted(probabilities.items()))
    plt.figure(figsize=(12, 6))
    plt.bar(patterns, probs, color='blue', alpha=0.7)
    plt.title(title, fontsize=14)
    plt.xlabel("Patterns", fontsize=12)
    plt.ylabel("Probability", fontsize=12)
    plt.xticks(rotation=90)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.show()

def generate_random_bits_ctr_drbg(sample_size):
    """
    Gera uma sequência de bits usando o CTR_DRBG.
    """
    aes_key_size_bits = 256
    entropy_input = os.urandom(128)
    generator = CTR_DRBG(aes_bits=aes_key_size_bits)
    generator.instantiate(entropy_input, generate_personalization_string())
    byte_sequence = generator.generate(sample_size)
    return bytes_to_bits(byte_sequence)

def generate_random_bits_fortuna(sample_size):
    """
    Gera uma sequência de bits usando o Fortuna.
    """
    aes_key_size_bits = 256
    aes_key_size_bytes = aes_key_size_bits // 8
    generator = FortunaGenerator(aes_key_size_bytes)
    accumulator = FortunaAccumulator()
    accumulator.add_random_event(1, os.urandom(32))  # Fonte 1
    accumulator.add_random_event(2, time.time_ns().to_bytes(8, 'big'))  # Fonte 2
    if accumulator.should_reseed():
        accumulator.reseed_generator(generator)
    byte_sequence = generator.generate(sample_size)
    return bytes_to_bits(byte_sequence)

def plot_histograms_for_algorithm(bit_sequence, algorithm_name, m):
    """
    Plota os histogramas para m-bit e (m+1)-bit para o algoritmo especificado.
    """
    # Histogram for m-bit blocks
    p_m = calculate_block_probabilities(bit_sequence, m)
    plot_histogram(p_m, f"{algorithm_name}: Histogram of {m}-bit Block Probabilities")

    # Histogram for (m+1)-bit blocks
    p_m_plus_1 = calculate_block_probabilities(bit_sequence, m + 1)
    plot_histogram(p_m_plus_1, f"{algorithm_name}: Histogram of {m+1}-bit Block Probabilities")

if __name__ == "__main__":
    sample_size = 1024  # Tamanho da sequência de bits
    m = 3  # Tamanho do bloco

    print("Generating histograms for CTR_DRBG...")
    ctr_drbg_bits = generate_random_bits_ctr_drbg(sample_size)
    plot_histograms_for_algorithm(ctr_drbg_bits, "CTR_DRBG", m)

    print("Generating histograms for Fortuna...")
    fortuna_bits = generate_random_bits_fortuna(sample_size)
    plot_histograms_for_algorithm(fortuna_bits, "Fortuna", m)
