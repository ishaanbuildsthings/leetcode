// https://leetcode.com/problems/3sum/description/
// Difficulty: Medium

// Solution
// O(n^2) time and O(1) or O(n) space depending on the sort implementation. Sort the list (log n) to allow us to do 2-sums in linear time. For every number in the list, do a 2-sum, hence n^2 time. If a target is the same as the target we just did, we would get a duplicate solution, so skip that. Once we find a solution, say [-2, 0, 0, 2, 5, 6], our target is -2 and we found a solution with 0 and 2, we need to move either the left or right pointer to try to find new solutions. It doesn't matter which you move, as they would both lead to a new possible sum. Say we move the left pointer from 0 to another 0, that's a repeat and must be avoided, so we keep incrementing. But if the left pointer ever reaches the right pointer, we also stop. We also wouldn't want the left pointer to go past the right pointer, as that would test nonseniscal triplets / triplets that could have been tested at other times.

const threeSum = function (numbers) {
  numbers = numbers.sort((a, b) => a - b);

  const solutions = [];
  // iterate over all numbers and do a 2-sum
  for (let i = 0; i < numbers.length - 2; i++) {
    if (i > 0 && numbers[i] === numbers[i - 1]) continue;

    // do a 2-sum
    const target = numbers[i];
    let l = i + 1;
    let r = numbers.length - 1;
    while (l < r) {
      if (target + numbers[l] + numbers[r] === 0) {
        solutions.push([target, numbers[l], numbers[r]]);
        l++;
        while (numbers[l] === numbers[l - 1] && l < r) {
          l++;
        }
      } else if (target + numbers[l] + numbers[r] > 0) {
        r--;
      } else {
        l++;
      }
    }
  }

  return solutions;
};
