// https://leetcode.com/problems/successful-pairs-of-spells-and-potions/description/
// Difficulty: Medium
// tags: binary search

// Problem
/*
You are given two positive integer arrays spells and potions, of length n and m respectively, where spells[i] represents the strength of the ith spell and potions[j] represents the strength of the jth potion.

You are also given an integer success. A spell and potion pair is considered successful if the product of their strengths is at least success.

Return an integer array pairs of length n where pairs[i] is the number of potions that will form a successful pair with the ith spell.

Input: spells = [5,1,3], potions = [1,2,3,4,5], success = 7
Output: [4,0,3]
Explanation:
- 0th spell: 5 * [1,2,3,4,5] = [5,10,15,20,25]. 4 pairs are successful.
- 1st spell: 1 * [1,2,3,4,5] = [1,2,3,4,5]. 0 pairs are successful.
- 2nd spell: 3 * [1,2,3,4,5] = [3,6,9,12,15]. 3 pairs are successful.
Thus, [4,0,3] is returned.
*/

// Solution, O(m log m + n log m) time and O(1) space. m log m time to sort the potions, and n log m time to binary search for each spell. Sort the potions, then do a binary search to find the smallest possible successful potion. Calculate the # of success and update result.

var successfulPairs = function (spells, potions, success) {
  potions.sort((a, b) => a - b);
  const result = new Array(spells.length).fill(null);

  for (let i = 0; i < spells.length; i++) {
    let l = 0;
    let r = potions.length - 1;
    while (l <= r) {
      const m = Math.floor((r + l) / 2); // represents the index of a potion we will try
      const strengthPower = spells[i] * potions[m];
      // if we were powerful enough, try a smaller potion
      if (strengthPower >= success) {
        r = m - 1;
      }
      // if our strength power is not enough, we need to try a bigger potion
      else if (strengthPower < success) {
        l = m + 1;
      }
    }
    const successful = potions.length - l;
    result[i] = successful;
  }
  return result;
};
