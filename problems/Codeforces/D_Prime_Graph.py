n = int(input())

N = 2*n
prime = [True] * (N + 1)
prime[0] = prime[1] = False
for number in range(2, N + 1):
    if not prime[number]: continue
    for mult in range(2 * number, N + 1, number):
        prime[mult] = False

edges = []
for node in range(1, n):
    edges.append([node, node + 1])
edges.append([n, 1])

numEdges = len(edges)
left = 1
right = n - 1
while not prime[numEdges]:
    edges.append([left, right])
    numEdges += 1
    left += 1
    right -= 1

print(len(edges))
for a, b in edges:
    print(f'{a} {b}')

