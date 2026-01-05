import sys
import random

data = list(map(int, sys.stdin.buffer.read().split()))
n, x = data[0], data[1]

seed = random.getrandbits(64)

mp = {0 ^ seed: 1}
res = tot = 0
get = mp.get

for v in data[2:]:
    tot += v
    requiredCutOff = tot - x
    res += get(requiredCutOff ^ seed, 0)

    key = tot ^ seed
    mp[key] = get(key, 0) + 1

sys.stdout.write(str(res))
