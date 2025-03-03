from binascii import hexlify

a = input()
if a == '':
    print('input required')
    exit()

a = hexlify(a.encode()).decode()
a = [f'%{a[i]}{a[i+1]}' for i in range(0, len(a), 2)]
a = ''.join(a)
print(a)