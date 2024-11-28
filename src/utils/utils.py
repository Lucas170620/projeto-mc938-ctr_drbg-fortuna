import random
import string
import time
from os import urandom

def registrar_log(mensagem):
    caminho_arquivo = "meu_log.txt"
    with open(caminho_arquivo, "a") as arquivo:
        arquivo.write(mensagem + "\n")

def generate_personalization_string():
    application_name = ''.join(random.choices(string.ascii_letters, k=8))  # 8 caracteres aleatórios
    device_id = ''.join(random.choices(string.ascii_letters + string.digits, k=12))  # 12 caracteres alfanuméricos
    random_suffix = urandom(8)
    personalization_string = f"{application_name}_{device_id}".encode() + random_suffix
    return personalization_string

def generate_nonce(security_strength):
    timestamp = int(time.time() * 1e6).to_bytes(8, byteorder="big")
    random_part = urandom(security_strength // 16)  # metade da força de segurança em bytes
    return timestamp + random_part


def xor(x,y):
    return bytes(a ^ b for a, b in zip(x, y))

def padding(_bytes,tamanho_esperado):
    return _bytes.ljust(tamanho_esperado, b"\x00")