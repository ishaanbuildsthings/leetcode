// https://leetcode.com/problems/replace-elements-with-greatest-element-on-right-side/description/
// Difficulty: Easy

// Solution
// O(n) time and O(1) space. Iterate over the array backwards, keeping track of the current greatest element. Replace the current element with the current greatest element, then update the current greatest element to be the current element.

var replaceElements = function (arr) {
  let currentGreatest = -1;

  for (let i = arr.length - 1; i >= 0; i--) {
    const temp = currentGreatest;

    if (arr[i] > currentGreatest) {
      currentGreatest = arr[i];
    }

    arr[i] = temp;
  }

  return arr;
};
