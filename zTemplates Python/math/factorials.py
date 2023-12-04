# MY FACTORIAL MOD TEMPLATE
# facs[i] = i! % MOD
# VARIABLES: MOD, N (highest factorial to compute)

MOD = 10**9 + 7 # change this
N = 10**5 # change this
facs = [1]
curr = 1
for i in range(N + 1):
  facs.append(curr)
  curr = (curr * i) % MOD