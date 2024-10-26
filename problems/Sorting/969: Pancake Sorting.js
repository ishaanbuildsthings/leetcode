// https://leetcode.com/problems/pancake-sorting/description/
// Difficulty: Medium
// Tags: sorting

// Problem
/*
Given an array of integers arr, sort the array by performing a series of pancake flips.

In one pancake flip we do the following steps:

Choose an integer k where 1 <= k <= arr.length.
Reverse the sub-array arr[0...k-1] (0-indexed).
For example, if arr = [3,2,1,4] and we performed a pancake flip choosing k = 3, we reverse the sub-array [3,2,1], so arr = [1,2,3,4] after the pancake flip at k = 3.

Return an array of the k-values corresponding to a sequence of pancake flips that sort arr. Any valid answer that sorts the array within 10 * arr.length flips will be judged as correct.
*/

// Solution, O(n^2) time and O(n) space
/*
For each number, starting at the highest, first put it in the front, then put it in its correct index.
*/

var pancakeSort = function (arr) {
  const result = [];

  let workingPancakes = [...arr]; // tracks the current state of the pancakes

  let lastToBeSolved = arr.length;
  while (lastToBeSolved > 1) {
    const position = workingPancakes.indexOf(lastToBeSolved);

    /*
        say we have [3, 2, 4, 1] and we are solving for 4, its position is i=2
        so we reverse [0, 2], getting [4, 2, 3, 1]
        */

    const reversedSubarray = workingPancakes.slice(0, position + 1).reverse();

    // now assign working pancakes to represent the new state
    workingPancakes = [
      ...reversedSubarray,
      ...workingPancakes.slice(position + 1),
    ];
    const numFlipped = position + 1;
    result.push(numFlipped);

    // now bring that number to its corret position

    const correctIndex = lastToBeSolved - 1;

    const reversedSub = workingPancakes.slice(0, correctIndex + 1).reverse();

    workingPancakes = [
      ...reversedSub,
      ...workingPancakes.slice(correctIndex + 1),
    ];
    const secondNumFlipped = correctIndex + 1;
    result.push(secondNumFlipped);

    lastToBeSolved--;
  }
  return result.filter((flip) => flip !== 0); // sincey sometimes I flip an element in the same place if it was already at the beginning, I just added a filter here since k>0 (though we could've handled that case)
};
