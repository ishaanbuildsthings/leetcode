MOD = 10**9 + 7
s = input()
n = len(s)
res = 0

def madd(a, b):
    return (a + b) % MOD

def mmult(a, b):
    return (a * b) % MOD

pow10Mod = [1]
for power in range(n + 1):
    npower = mmult(pow10Mod[-1], 10)
    pow10Mod.append(npower)

# how many substrings exist in a string of length x
def substrings(x):
    return x * (x + 1) // 2

right = 0

for i in range(n - 1, -1, -1):
    d = int(s[i])
    onLeft = i
    # for any substring deleted on the left, this maintains its power contribution
    substringsOnLeft = substrings(onLeft)
    # for each of those substrings, we keep our contribution

    power = n - i - 1
    contribution = mmult(d, pow10Mod[power])
    gainLeft = mmult(substringsOnLeft, contribution)
    res = madd(res, gainLeft)

    gainRight = mmult(d, right)
    res = madd(res, gainRight)

    upDigit = (n - i - 1) + 1
    upGain = upDigit * pow10Mod[upDigit - 1]
    right = madd(right, upGain)
   

print(res)
