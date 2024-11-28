

def bytes_to_bits(byte_data):
    return ''.join(f'{byte:08b}' for byte in byte_data)

a_b = b'\xde<\xb6\x02mz"\xb1\xdc\xcb\xc7\xb1\x1e\x10=\x8eU;A\x14\xd6[e"u\xa6\xea\xfb#\x16\x1e\xec'
b_b = b'nLlerBta_8DHbC8oCqEqx\x07 p\\ir\x015\x00\x00\x00'
c_b = b'\xb0p\xdag\x1f8V\xd0\x83\xf3\x83\xf9|S\x05\xe1\x16J\x04e\xae\\ER)\xcf\x98\xfa\x16\x16\x1e\xec'
a = bytes_to_bits(a_b)
b = bytes_to_bits(b_b)
r = bytes_to_bits(c_b)

temp = True
for i in range(len(a)):
    t = abs(int(a[i])-int(b[i]))
    if t != int(r[i]):
        temp = False
        print(i)
print(temp)

