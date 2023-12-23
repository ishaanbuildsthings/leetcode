// https://leetcode.com/problems/count-vowels-permutation/description/
// Difficulty: Hard
// tags: dynamic programming 2d, top down recursion

// Problem
/*
Example:
Input: n = 2
Output: 10
Explanation: All possible strings are: "ae", "ea", "ei", "ia", "ie", "io", "iu", "oi", "ou" and "ua".

Detailed:
Given an integer n, your task is to count how many strings of length n can be formed under the following rules:

Each character is a lower case vowel ('a', 'e', 'i', 'o', 'u')
Each vowel 'a' may only be followed by an 'e'.
Each vowel 'e' may only be followed by an 'a' or an 'i'.
Each vowel 'i' may not be followed by another 'i'.
Each vowel 'o' may only be followed by an 'i' or a 'u'.
Each vowel 'u' may only be followed by an 'a'.
Since the answer may be too large, return it modulo 10^9 + 7.
*/

// Solution, O(n) time and O(n) space.
/*
Allocate a 5*n matrix where memo[len][vowelNum] indiciates the amount of valid permutations of length `len` that start with the appropriate vowel. There are 5n states, and each takes a constant amount of time to solve, so the total time is O(n). The recurrence function is given by the problem.
*/

const VOWELS = {
  0: "a",
  1: "e",
  2: "i",
  3: "o",
  4: "u",
};

const MOD = 10 ** 9 + 7;

var countVowelPermutation = function (n) {
  // memo[len][vowelNum] represents the number of strings that can be formed of length `len` that start with a given vowel
  const memo = new Array(n + 1).fill().map(() => new Array(5).fill(-1));

  function dp(len, vowelNum) {
    if (memo[len][vowelNum] !== -1) {
      return memo[len][vowelNum];
    }

    // base case
    if (len === 1) {
      return 1;
    }

    let resultForThisDp = 0;

    if (vowelNum === 0) {
      resultForThisDp = dp(len - 1, 1); // a is followed by e
    } else if (vowelNum === 1) {
      resultForThisDp = (dp(len - 1, 0) + dp(len - 1, 2)) % MOD; // e is followed by a or i
    } else if (vowelNum === 2) {
      // i is followed by everything except i
      const dps = [0, 1, 3, 4].map((num) => dp(len - 1, num));
      for (let dpAmount of dps) {
        resultForThisDp = (resultForThisDp + dpAmount) % MOD;
      }
    } else if (vowelNum === 3) {
      resultForThisDp = (dp(len - 1, 2) + dp(len - 1, 4)) % MOD;
    } else if (vowelNum === 4) {
      resultForThisDp = dp(len - 1, 0);
    }

    memo[len][vowelNum] = resultForThisDp;
    return resultForThisDp;

    /*
        the answer to a problem of `len` with a starting vowel of `VOWELS[vowelNum]` is given by the recurrence function in the problem
        */
  }

  let MAX_VOWEL_COUNT = 4;
  let result = 0;
  for (
    let startingVowel = 0;
    startingVowel <= MAX_VOWEL_COUNT;
    startingVowel++
  ) {
    result = (result + dp(n, startingVowel)) % MOD;
  }

  return result;
};
