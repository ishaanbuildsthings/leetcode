// https://leetcode.com/problems/make-array-strictly-increasing/description/
// Difficulty: Hard
// tags: binary search, dynamic programming 1d

// Problem
/*
Simplified:
Example 1:

Input: arr1 = [1,5,3,6,7], arr2 = [1,3,2,4]
Output: 1
Explanation: Replace 5 with 2, then arr1 = [1, 2, 3, 6, 7].
Example 2:

Input: arr1 = [1,5,3,6,7], arr2 = [4,3,1]
Output: 2
Explanation: Replace 5 with 3 and then replace 3 with 4. arr1 = [1, 3, 4, 6, 7].

Detailed:
Given two integer arrays arr1 and arr2, return the minimum number of operations (possibly zero) needed to make arr1 strictly increasing.

In one operation, you can choose two indices 0 <= i < arr1.length and 0 <= j < arr2.length and do the assignment arr1[i] = arr2[j].

If there is no way to make arr1 strictly increasing, return -1.
*/

// Solution, O(m log m + n^2*log m) time. Max(O(n), O(sort m)) space.
/*
Consider 1,5,3,6,7 and arr2 = 1,3,4

Start at the first index. If we make 0 changes, the number to beat is 1 in the future. If we make 1 change, it is 3. { 0 : 1, 1 : 3 }
At the 5, we can make 2 changes for the first time. If we do, we need to beat 4 now, because 4 is the smallest number larger than 3 from 1 change. We can also make 1 change by keeping the 5 as is, or by making a change on top of the previous 0 change, we pick the minimum. If we cannot validly make some amount of changes, we set it to -1. For instance in [1, 5] arr2 = 6, we cannot make 1 change at the bery beginning. But later we can make 1 change by overriding the 5. The code is somewhat messy, a slightly better implementation would have populated the initial dp map with -1 : 0, so our 0th number has to beat a 0.

We sort arr2, m log m time. Then we iterate over n, for each n, we iterate up to n prior change amounts, and do a log m binary search.
*/

var makeArrayIncreasing = function (arr1, arr2) {
  // sort the options we can use so we can binary search them
  arr2.sort((a, b) => a - b);

  const mapping = { 0: arr1[0] }; // maps the number of changes to the best our previous number could be, holds up to n changes.

  for (let i = 0; i < arr1.length; i++) {
    // if we are at index 0, we should consider making 0 changes and making 1 change with the new number
    /*
        we need to iterate over changes backwards, consider:

        1, 5   we can change to anything
        if we do 0 changes, number to beat = 1.  0 : 1
        now at 5, if we do 0 changes, number to beat = 5. 0 : 5
        but if we try 1 change, we should have greedy selected against 1, not 5.
        */
    for (let changes = i + 1; changes >= 0; changes--) {
      // if we are allowed to make a change to the very first number, just make that number the smallest one
      if (changes === 1 && i === 0) {
        mapping[1] = arr2[0];
        continue;
      }
      // if we want to make 0 changes, we will just compare among the 0 change number
      if (changes === 0) {
        // we don't have to process making 0 changes at the first element, as we store that in the mapping already
        if (i === 0) {
          continue;
        }

        // if 0 changes were already impossible, just continue
        if (mapping[0] === -1) {
          continue;
        }

        // if 0 changes were previously possible, we need to check if our new number is bigger
        const num = arr1[i];
        if (num > mapping[0]) {
          mapping[0] = num; // in the future we will have to beat this
        } else {
          mapping[0] = -1; // if we can't continue the 0 changes streak, 0 is impossible
        }
        continue;
      }
      /* here, changes are 1 or more */

      /*
            if this is the first time making a new highest amount of changes, all we can do is greedy select from the prior change amount
            */
      if (changes === i + 1) {
        const prevChangeNum = mapping[changes - 1];
        // if we couldn't use the previous change amount, we won't be able to use the new one
        if (prevChangeNum === -1) {
          mapping[changes] = -1;
          continue;
        }
        const smallestLarger = findSmallestLarger(arr2, prevChangeNum);
        // if even changing every number up until that subarray doesn't work, we can never make a valid arrangement
        if (smallestLarger === null) {
          mapping[changes] = -1;
          continue;
        }

        mapping[changes] = smallestLarger;
        continue;
      }
      /* here, changes is between 1 but not a brand new change amount */

      /*
                say we want to make 1 change, we can either use 0 changes from before, and greedy select
                or use 1 change from before, and take our current number
            */

      // option 1, greedy select over the previous smallest
      const prevChangeNum = mapping[changes - 1];
      let smallestLarger;
      // if we couldn't use the previous amount, we cannot greedily select, setting to null will invalidate option 1
      if (prevChangeNum === -1) {
        smallestLarger = null;
      } else {
        smallestLarger = findSmallestLarger(arr2, prevChangeNum);
      }

      // option 2, don't change anything, use the current number
      let canUseOptionTwo;
      // if we don't change anything, but we already couldn't use that many changes, we still cannot
      if (mapping[changes] === -1) {
        canUseOptionTwo = false;
      } else {
        canUseOptionTwo = arr1[i] > mapping[changes]; // if our new number is bigger, we don't need to change anything
      }

      // if both options are valid
      if (smallestLarger !== null && canUseOptionTwo) {
        const minimum = Math.min(smallestLarger, arr1[i]);
        mapping[changes] = minimum;
      }

      // if just the first is valid
      else if (smallestLarger !== null) {
        mapping[changes] = smallestLarger;
      }

      // if just the second is valid
      else if (canUseOptionTwo) {
        mapping[changes] = arr1[i];
      }

      // if neither is valid, it is impossible to use that many changes
      else {
        mapping[changes] = -1;
      }
    }
  }

  for (const key in mapping) {
    if (mapping[key] !== -1) {
      return key;
    }
  }

  return -1;
};

// finds the smallest number that is larger than n in arr, or returns null if it is not possible
function findSmallestLarger(arr, n) {
  let l = 0;
  let r = arr.length - 1;
  while (l < r) {
    const m = Math.floor((r + l) / 2);
    const num = arr[m];
    if (num > n) {
      r = m;
    } else {
      l = m + 1;
    }
  }

  if (arr[r] > n) {
    return arr[r];
  }

  return null;
}
