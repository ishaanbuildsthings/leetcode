// https://leetcode.com/problems/can-place-flowers/description/
// Difficulty: Easy

// Problem
/*
You have a long flowerbed in which some of the plots are planted, and some are not. However, flowers cannot be planted in adjacent plots.

Given an integer array flowerbed containing 0's and 1's, where 0 means empty and 1 means not empty, and an integer n, return true if n new flowers can be planted in the flowerbed without violating the no-adjacent-flowers rule and false otherwise.
*/

// Solution
// O(n) time and O(1) space. This solution mutates the input array but we could not mutate it too, and instead track a previous pot variable. So whenever we plant a pot, instead of mutating the array, we set the previous pot to say it is planted. The solution iterates over the flowers, and if we are at a 0, if the previous is a 0 or we are at the beginning, and the next is a 0 or we are at the end, we can place a flower.

var canPlaceFlowers = function (flowerbed, n) {
  // edge case, wouldn't be handled inside the loop
  if (n === 0) {
    return true;
  }

  let totalPlaced = 0;
  for (let i = 0; i < flowerbed.length; i++) {
    if (flowerbed[i] === 1) {
      continue;
    }
    // we are at a 0, if the previous is a 0 or we are at the beginning, and the next is a 0 or we are at the end, we can place
    if (
      (flowerbed[i - 1] === 0 || i === 0) &&
      (flowerbed[i + 1] === 0 || i === flowerbed.length - 1)
    ) {
      flowerbed[i] = 1;
      totalPlaced++;
      if (totalPlaced === n) {
        return true;
      }
    }
  }
  return false;
};
