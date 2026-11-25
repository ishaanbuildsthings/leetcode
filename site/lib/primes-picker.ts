import type { PickerOpGroup } from "@/components/OpPicker";

// The Primes tab's op picker (templates/ultimate-template-tool/primes/Primes.*): grouped by the question you're asking.
// Every op's cost and practical limit is measured, not guessed (primes-tests/test_primes.py checks the answers).
export const PRIMES_GITHUB = "https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/primes/";

export const PRIMES_GROUPS: PickerOpGroup[] = [
  {
    title: "One big number: no setup, any x < 2^64",
    ops: [
      {
        id: "isPrime",
        call: "isPrime(x)",
        returns: "True if x is prime",
        example: "isPrime(10**18 + 9) -> True, isPrime(561) -> False",
        note: "deterministic Miller-Rabin: exact, not probabilistic",
        cost: "log(x)",
      },
      {
        id: "primeFactorize",
        call: "primeFactorize(x)",
        returns: "[(prime, exponent), ...] sorted by prime",
        example: "primeFactorize(360) -> [(2, 3), (3, 2), (5, 1)]; primeFactorize(1) -> []",
        note: "Pollard rho, randomized: about x^(1/4) expected, fine for any 64-bit x. The largest prime factor is the last pair",
        cost: "x^(1/4)",
      },
      {
        id: "allFactors",
        call: "allFactors(x)",
        returns: "every positive divisor of x, UNSORTED",
        example: "allFactors(12) -> [1, 2, 4, 3, 6, 12]",
        note: "factorizes with primeFactorize, then builds the divisors; D = number of divisors; sort it yourself if you need an order (D log D)",
        cost: "x^(1/4)+D",
      },
    ],
  },
  {
    title: "Many small numbers: build the sieve once, O(N · log(log N))",
    setup: { call: "sieve = PrimeSieve(N)", returns: "build; then x can be anything from 0 up to N, memory ~5N bytes", cost: "N*log(log(N))" },
    ops: [
      {
        id: "sieveIsPrime",
        call: "sieve.isPrime(x)",
        returns: "True if x is prime",
        example: "sieve.isPrime(97) -> True",
        note: "needs x <= N",
        cost: "1",
      },
      {
        id: "sieveSmallestPrimeFactor",
        call: "sieve.smallestPrimeFactor(x)",
        returns: "the smallest prime dividing x",
        example: "sieve.smallestPrimeFactor(91) -> 7",
        note: "needs 2 <= x <= N",
        cost: "1",
      },
      {
        id: "sieveFactorize",
        call: "sieve.primeFactorize(x)",
        returns: "[(prime, exponent), ...] sorted by prime",
        example: "sieve.primeFactorize(360) -> [(2, 3), (3, 2), (5, 1)]",
        note: "needs 1 <= x <= N; the largest prime factor is the last pair",
        cost: "log(x)",
      },
      {
        id: "sieveAllFactors",
        call: "sieve.allFactors(x)",
        returns: "every positive divisor of x, UNSORTED",
        example: "sieve.allFactors(12) -> [1, 2, 4, 3, 6, 12]",
        note: "needs 1 <= x <= N; D = number of divisors; sort it yourself if you need an order (D log D)",
        cost: "log(x)+D",
      },
      {
        id: "sieveFactorizeUpToNSquared",
        call: "sieve.primeFactorizeUpToNSquared(x)",
        returns: "[(prime, exponent), ...] sorted by prime",
        example: "with N = 10^6: sieve.primeFactorizeUpToNSquared(999962000357) -> [(999979, 1), (999983, 1)]",
        note: "needs x <= N^2 (sieve to 10^6, factor up to 10^12): trial division by the sieved primes up to sqrt(x); what's left is 1 or one prime",
        cost: "sqrt(x)/log(x)",
      },
      {
        id: "sievePrimes",
        call: "sieve.primes",
        returns: "every prime <= N, increasing",
        example: "PrimeSieve(20).primes -> [2, 3, 5, 7, 11, 13, 17, 19]",
        note: "the same list primesUpTo(N) gives, here for free because the sieve is already built (with its smallest-prime-factor table)",
        cost: "1",
      },
    ],
  },
  {
    title: "Listing primes",
    ops: [
      {
        id: "primesUpTo",
        call: "primesUpTo(N)",
        returns: "every prime <= N, increasing",
        example: "primesUpTo(20) -> [2, 3, 5, 7, 11, 13, 17, 19]",
        note: "just the list, without the sieve's smallest-prime-factor table, so it needs far less memory: C++ reaches N = 10^9 in ~1s (its 50,847,534 primes ~200 MB; a PrimeSieve that big would need ~4 GB). Python: N = 10^8 in ~2.5s",
        cost: "N*log(log(N))",
      },
      {
        id: "primesInRange",
        call: "primesInRange(lo, hi)  (segmented sieve)",
        returns: "every prime p with lo <= p <= hi, increasing",
        example: "primesInRange(10**12, 10**12 + 100) -> [1000000000039, 1000000000061, 1000000000063, 1000000000091]",
        note: "segmented sieve: crosses off multiples of the primes up to sqrt(hi) inside just that window, so hi can be ~10^12 as long as hi - lo is ~10^7 or less",
        cost: "(hi-lo)*log(log(hi))+sqrt(hi)",
      },
    ],
  },
  {
    title: "Counting primes without listing them",
    ops: [
      {
        id: "countPrimes",
        call: "countPrimes(n)",
        returns: "how many primes are <= n",
        example: "countPrimes(100) -> 25; countPrimes(10**9) -> 50847534",
        note: "Lucy_Hedgehog, O(sqrt n) memory. C++: n = 10^12 in ~0.2s, 10^13 in ~1s; Python: 10^10 in ~1s",
        cost: "n^(3/4)",
      },
    ],
  },
];
