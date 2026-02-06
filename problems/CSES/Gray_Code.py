n = int(input())
for number in range(1 << n):
    gray = number ^ (number >> 1)
    print(bin(gray)[2:].zfill(n))

    