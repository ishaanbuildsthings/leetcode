// https://leetcode.com/problems/random-pick-with-weight/description/
// Difficulty: Medium
// Tags: binary search

// Problem
/*
You are given a 0-indexed array of positive integers w where w[i] describes the weight of the ith index.

You need to implement the function pickIndex(), which randomly picks an index in the range [0, w.length - 1] (inclusive) and returns it. The probability of picking an index i is w[i] / sum(w).

For example, if w = [1, 3], the probability of picking index 0 is 1 / (1 + 3) = 0.25 (i.e., 25%), and the probability of picking index 1 is 3 / (1 + 3) = 0.75 (i.e., 75%).
*/

// Solution, O(n) time to construct, O(log n) time to pick. O(n) space for construction.
/*
We have elements with different chances to occur. We want to pick a random number essentially, and figure out which element it should fall in. We can make buckets for the elements, so if the chances are: 25%, 25%, 30%, 20%, buckets are: 0-25, 25-50, 50-80, 80-100. Then we can pick a random number between 0 and 100, and see which bucket it falls in. We can use a binary search to find the bucket.
*/

/**
 * @param {number[]} w
 */
var Solution = function (w) {
  const sum = w.reduce((acc, val) => acc + val, 0);
  const chances = w.map((weight) => weight / sum); // [0.33, 0.33, 0.167, 0.167]

  this.prefixChances = []; // [0.33, 0.66, 0.83, 1.00]
  let runningSum = 0;
  for (let i = 0; i < chances.length; i++) {
    runningSum += chances[i];
    this.prefixChances.push(runningSum);
  }
};

/**
 * @return {number}
 */
Solution.prototype.pickIndex = function () {
  const rand = Math.random();

  // do a binary search to find the first number in the prefix chances that is bigger than our current number, meaning we fall in that bucket

  let l = 0;
  let r = this.prefixChances.length - 1;

  while (l < r) {
    const m = Math.floor((r + l) / 2); // m is the index of the chance we are looking at

    const boundary = this.prefixChances[m];

    if (boundary > rand) {
      r = m;
    } else {
      l = m + 1;
    }
  }

  return r;
};

/**
 * Your Solution object will be instantiated and called as such:
 * var obj = new Solution(w)
 * var param_1 = obj.pickIndex()
 */
