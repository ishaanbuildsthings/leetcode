# All sequences of length 2N must have N open and N closed brackets
# There are 2N choose N ways to construct these (place all opens somewhere, remaining ones are closed)
# However, we need to exclude sequences with prefixes that have more closed than open brackets, like ( ) ) (

# This is sufficient to compute good bracket sequences, why?

# Necessary
# If a prefix contains more closed than open brackets, it is impossible for that closed bracket to ever be paired with something
# Sufficient
# Every prefix will have at least as many open as closed, we maintain a counter of surplus open
# Any time we encounter a closed bracket we will have at least 1 open bracket, and can decrement the counter
# Therefore every closed bracket decrements the counter by 1 and is paired with something
# All closed brackets will get paired with something safely and we will end up with a final surplus of 0 implying all open brackets were paired

# Now we need to compute the prefix-violating bracket sequences
# Write all bracket sequences, e.g. n=4
# For each sequence, if it is bad we find the index it first has more closed than open, this prefix has 1 more closed than open bracket
# The suffix therefore has 1 more open than closed bracket
# We invert the prefix, now the total sequence has 2 more open than closed brackets, or more generally N+1 open and N-1 closed
# ()() ✓
# (()) ✓
# ()) | (  ->  )(( | (
# ) | ()(  -> ( | ()(
# ) | )((  -> ( | )((
# ) | )()  -> ( | )()

# There are 2N choose N+1 of these resulting sequences. We are claiming we map a bijection to all possible resulting sequences.
# If a function is injective (every input maps to a unique output) and surjective (every output is mapped to by an input) then it is bijective.

# First show that it is injective, obviously every input has a different output. If two inputs had the same output, we can locate the different input bracket and show that it must produce two differing outputs, violating the claim.
# To show it is surjective, we work backwards. From 2N choose N+1 sequence (N+1 opening brackets), we can find the first prefix with more opening than closing brackets and re-invert that, producing an input with a prefix of more closing brackets than opening brackets, showing we can produce a state that maps to this.

# Therefore, this is bijective.

# So the final answer is C(2N, N) - C(2N, N - 1)

MAX_N = 10**6
MOD = 10**9 + 7
fact = [1] # 0! % MOD
for num in range(1, MAX_N + 1):
    nfac = (fact[-1] * num) % MOD
    fact.append(nfac)

invFact = [1] * (MAX_N + 1)
invFact[MAX_N] = pow(fact[MAX_N], MOD - 2, MOD)
for i in range(MAX_N, 0, -1):
    invFact[i - 1] = invFact[i] * i % MOD

def nCkMod(n, k):
    if k < 0 or k > n:
        return 0
    return fact[n] * invFact[k] % MOD * invFact[n - k] % MOD

N = int(input())
if N % 2:
    print(0)
    exit()

print((nCkMod(N, N // 2) - nCkMod(N, (N // 2) - 1)) % MOD)

