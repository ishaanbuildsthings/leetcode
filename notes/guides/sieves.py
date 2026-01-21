"""
Find all primes in [1, n] with O(n log log n) time using the classic Sieve of Eratosthenes.

-Write down all numbers from 2 to N.
-Mark all proper multiples of 2 as composite
-Find the next unmarked number (3) and mark all its proper multiplies
-Once done we will have all primes.

Proving O(n log n) runtime is easy as it acts like a harmonic sum. The 2 can contribute at most n/2 operations, the 3 n/3, and so on.

There is some more complex proof for O(n log log n) I don't know
"""

"""
Part 2: Optimizations

------------
Sieving till root:

A downside is that we "walk" along the memory multiple times only manipulating single elements which is not cache friendly.
So the constant factor on O(n log log n) is comparably big. And the memory N is a big bottleneck.

We don't need to run the sift up for any numbers > root N. Like if N=100 and we start sifting up from 13 it would only mark numbers as not prime that have a factor < rootN (since we cannot have two differerent factors >= rootN)

With the simple harmonic series complexity proof we would now get:
N + N/2 + N/3 + .... + N/rootN

This ends up being 1/2*(N log N) + N somehow which is still N log N (but definitely faster).
But the tighter upper bound becomes N*(log log rootN + O(1)) = N log log N + N which is the same asymptotically but much faster.

------------
Sieving odds only

We don't have to check even numbers at all since they will be non-prime except for 2. So we can increment by 2 or even reduce our memory by 2x (need to virtualize the indices to handle odd->all number mapping sort of, like isPrimeOdd[number])

------------
C++ vector<bool> vs vector<char>

Don't use vector<bool> since it does some weird stuff under the hood. https://cp-algorithms.com/algebra/sieve-of-eratosthenes.html#memory-consumption-and-speed-of-operations

------------
Segmented Sieve

We want to know which numbers from L...R are prime for big L and R, but R-L is still manageable.

Say L = 1e9 and R = L + 1e6.

We create a sieve of size 1e6 representing the numbers from L to R.

We generate a normal sieve up to root(R).

We only need to sift up all of those primes, why would we not need to sift up a prime > root(R)? Because if we marked a number with that prime it would necessarily have another factor < root(R).

Let us establish a loose upper bound on the complexity of this. Recall H_n (harmonic) is roughly log N. 1 + 1/2 + 1/3 + .... + 1/n. And n + n/2 + n/3 + ... is n log n.

If worst case every single number from 1 to rootR was prime (obviously most are not) then we loop over all of those, and the work each "prime" would do is W/p (W = width)
We wish to sum these for all numbers 1 to rootR, we can factor out the W.

So W * Sigma(1/p) for all p up to rootR.
That harmonic is log rootR. Times the outside W is W log (rootR) which is W log R. This generates the segmented sieve after the initial sieve up to rootR is computed.

The real complexity is W log log R (I have no idea how)
"""