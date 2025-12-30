T = int(input())
for _ in range(T):
    n = int(input())
    s = input()

    def sv():
        if '2026' in s:
            return 0
        if '2025' in s:
            return 1
        return 0

    print(sv())
