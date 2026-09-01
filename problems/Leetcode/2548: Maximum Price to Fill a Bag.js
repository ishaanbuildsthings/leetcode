// https://leetcode.com/problems/maximum-price-to-fill-a-bag/description/
// difficulty: Medium
// tags: greedy

// Problem
/*
You are given a 2D integer array items where items[i] = [pricei, weighti] denotes the price and weight of the ith item, respectively.

You are also given a positive integer capacity.

Each item can be divided into two items with ratios part1 and part2, where part1 + part2 == 1.

The weight of the first item is weighti * part1 and the price of the first item is pricei * part1.
Similarly, the weight of the second item is weighti * part2 and the price of the second item is pricei * part2.
Return the maximum total price to fill a bag of capacity capacity with given items. If it is impossible to fill a bag return -1. Answers within 10-5 of the actual answer will be considered accepted.
*/

// Solution, O(n log n) time, O(sort) space
/*
Just take the highest value (by price/weight) items first, then split the last item if it doesn't fit perfectly.

First, sort all items, so O(n log n) time and O(sort) space. Then, while the bag isn't full, add items, at most every item.
*/

var maxPrice = function (items, capacity) {
  items.sort((a, b) => {
    const [price1, weight1] = a;
    const [price2, weight2] = b;
    if (price1 / weight1 >= price2 / weight2) {
      return -1;
    } else {
      return 1;
    }
  });

  let spacedUsed = 0;
  let result = 0;
  let itemPointer = 0;
  // fill items while they can entirely fit, and stay under capacity
  while (spacedUsed + items[itemPointer][1] < capacity) {
    const [itemPrice, itemWeight] = items[itemPointer];
    spacedUsed += itemWeight;
    result += itemPrice;
    itemPointer++;
    // if we ever run out of items, and we still fit under capcity, we return -1
    if (itemPointer === items.length) {
      return -1;
    }
  }

  // then, add the fractional item
  const [itemPrice, itemWeight] = items[itemPointer];
  const weightNeeded = capacity - spacedUsed;
  const ratio = weightNeeded / itemWeight;

  result += ratio * itemPrice;

  return result;
};
