// https://leetcode.com/problems/count-good-meals/description/
// Difficulty: Medium

// Problem
/*
A good meal is a meal that contains exactly two different food items with a sum of deliciousness equal to a power of two.

You can pick any two different foods to make a good meal.

Given an array of integers deliciousness where deliciousness[i] is the deliciousness of the i​​​​​​th​​​​​​​​ item of food, return the number of different good meals you can make from this list modulo 109 + 7.

Note that items with different indices are considered different even if they have the same deliciousness value.
*/

// Solution, O(n) time and O(n) space
/*
Gather a count of how many time each number occurs. For each number, and for each power of 2 up to the specified max (we treat this as a constant), check how many other numbers there are we can use to make that power of two. Also decrement the count of each number as we iterate, to not count duplicate pairs.
*/

const powersOfTwo = [];

for (let power = 0; power <= 21; power++) {
  powersOfTwo.push(2 ** power);
}

var countPairs = function (deliciousness) {
  const counts = {}; // maps a number to how many times it occurs

  for (const num of deliciousness) {
    if (!(num in counts)) {
      counts[num] = 1;
    } else {
      counts[num]++;
    }
  }

  let result = 0;

  for (const num of deliciousness) {
    counts[num]--;
    for (const power of powersOfTwo) {
      const needed = power - num;
      if (needed in counts) {
        result += counts[needed];
      }
    }
  }

  return result % (10 ** 9 + 7);
};
