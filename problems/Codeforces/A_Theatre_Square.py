import math

inputArr = input().split(' ')

n, m, a = inputArr
n = int(n)
m = int(m)
a = int(a)

# n*m square

width = math.ceil(n/a)
height = math.ceil(m/a)
print(width * height)