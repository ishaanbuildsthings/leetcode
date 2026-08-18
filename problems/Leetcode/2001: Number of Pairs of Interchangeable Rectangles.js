// https://leetcode.com/problems/number-of-pairs-of-interchangeable-rectangles/description/
// Difficulty: Medium
// tags: arrays

// Problem
/*
You are given n rectangles represented by a 0-indexed 2D integer array rectangles, where rectangles[i] = [widthi, heighti] denotes the width and height of the ith rectangle.

Two rectangles i and j (i < j) are considered interchangeable if they have the same width-to-height ratio. More formally, two rectangles are interchangeable if widthi/heighti == widthj/heightj (using decimal division, not integer division).

Return the number of pairs of interchangeable rectangles in rectangles.
*/

// Solution, O(n) time and O(n) space
/*
This question is essentially asking how many distinct fractions we have. Compute a decimal for each pair, adding it to a mapping. Then iterate through each mapped decimal and add to the result.
*/

var interchangeableRectangles = function (rectangles) {
  let result = 0;

  const mapping = {}; // maps decimals to the amount of times they have occured
  for (const rectangle of rectangles) {
    const decimal = rectangle[0] / rectangle[1];
    if (decimal in mapping) {
      mapping[decimal]++;
    } else {
      mapping[decimal] = 1;
    }
  }

  for (const decimal in mapping) {
    const count = mapping[decimal];
    const pairs = (count * (count - 1)) / 2;
    result += pairs;
  }

  return result;
};
