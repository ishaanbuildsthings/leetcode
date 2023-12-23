// https://leetcode.com/problems/top-k-frequent-elements/description/
// Difficulty: Medium
// tags: bucket sort

// Problem
/*
Given an integer array nums and an integer k, return the k most frequent elements. You may return the answer in any order.
*/

// Solution
// Time: O(n), space: O(n)
/*
Say we have some list of numbers: [1, 1, 1, 3, 5, 7, 7] and we need to find the 2 most common numbers

We can use a hash map to count the frequency of each number: { 1: 3, 3: 1, 5: 1, 7: 2 }

We can then create a map for the # of occurences to a list of numbers that fall under that many occurences:
{ 3: [1], 1: [3, 5], 2: [7] }

This could also be an array, and we use the # of occurences as the index of the array.

This works, because the max # of occurences is n, since a number can occur at most n times (it would be every number in the array)

Now, we simply iterate over the array or object from the end, and add the numbers to the output array until we have k numbers.

The inner for loop is amortized, since we can have at most n distinct types of elements

*/

const topKFrequent = function (nums, k) {
  // track how many times each number occurs
  const numsToOccurences = {};
  for (const num of nums) {
    if (num in numsToOccurences) {
      numsToOccurences[num]++;
    } else {
      numsToOccurences[num] = 1;
    }
  }

  // reverse it, map a count of occurences to a list of the numbers that occured that many times

  const occurencesToNums = {};

  for (const numKey in numsToOccurences) {
    const occurences = numsToOccurences[numKey];
    if (occurences in occurencesToNums) {
      occurencesToNums[occurences].push(numKey);
    } else {
      occurencesToNums[occurences] = [numKey];
    }
  }

  const kMostFrequent = [];

  let i = nums.length; // at most, a number can occure nums.length times, so we will start from there, and iterate down until we get the k most frequent elements
  while (i > 0) {
    if (i in occurencesToNums) {
      const numList = occurencesToNums[i];
      for (let j = 0; j < numList.length; j++) {
        kMostFrequent.push(numList[j]);
        if (kMostFrequent.length === k) {
          return kMostFrequent;
        }
      }
    }
    i--;
  }
};
