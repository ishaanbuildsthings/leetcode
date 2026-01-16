banned = [2]
while banned[-1] <= 1000000000:
    banned.append(banned[-1] * 4)
banned = set(banned)

t = int(input())
for _ in range(t):
    n = int(input())
    if n % 2:
        print("Bob")
        continue
    if n in banned:
        print("Bob")
        continue
    print("Alice")