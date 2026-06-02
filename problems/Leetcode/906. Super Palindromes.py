pals = []
for num in range(10**5 + 1):
    first = str(num) + str(num)[::-1]
    if first == first[::-1]:
        pals.append(first)
    for mid in range(10):
        second = str(num) + str(mid) + str(num)[::-1]
        if second == second[::-1]:
            pals.append(second)
supers = []
for pal in pals:
    squared = int(pal)**2
    squaredStr = str(squared)
    if squaredStr == squaredStr[::-1]:
        supers.append(squaredStr)
supers.append(1)
supers.append(4)
supers.append(9)
supers = sorted(set(int(s) for s in supers))

class Solution:
    def superpalindromesInRange(self, left: str, right: str) -> int:
        return sum(
            num >= int(left) and num <= int(right) for num in supers
        )