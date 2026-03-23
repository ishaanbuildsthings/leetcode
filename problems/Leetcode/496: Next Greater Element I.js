// https://leetcode.com/problems/next-greater-element-i/description/
// Difficulty: Easy
// tags: monotonic stack

// Problem
/*
Simplfied:
Input: nums1 = [4,1,2], nums2 = [1,3,4,2]
Output: [-1,3,-1]
Explanation: The next greater element for each value of nums1 is as follows:
- 4 is underlined in nums2 = [1,3,4,2]. There is no next greater element, so the answer is -1.
- 1 is underlined in nums2 = [1,3,4,2]. The next greater element is 3.
- 2 is underlined in nums2 = [1,3,4,2]. There is no next greater element, so the answer is -1.

Detailed:
The next greater element of some element x in an array is the first greater element that is to the right of x in the same array.

You are given two distinct 0-indexed integer arrays nums1 and nums2, where nums1 is a subset of nums2.

For each 0 <= i < nums1.length, find the index j such that nums1[i] == nums2[j] and determine the next greater element of nums2[j] in nums2. If there is no next greater element, then the answer for this query is -1.

Return an array ans of length nums1.length such that ans[i] is the next greater element as described above.
*/

// Solution, O(n) time and O(n) space

/*
Iterate through nums 2, maintaining a monotonic decreasing stack. For instance say we start with [7, 5, 3] in nums2, so we add all of those to our stack. Then, we see a 6, which is a next greater element because it doesn't keep decreasing. Keep popping elements off the stack until we can make it monotonically decreasing again. Every time we pop an element, we add that element : bigger number into a hash map. For instance we pop off 3 because it was beaten by a 6, so we add {3:6}. We can do this since the elements are unique. Then we iterate over nums1, do lookups in the hashmap, and construct the output.
*/
var nextGreaterElement = function (nums1, nums2) {
  const stack = []; // used to find the next greatest elements
  const mapping = {}; // maps numbers to their next greatest elements

  for (let i = 0; i < nums2.length; i++) {
    while (stack.length > 0 && nums2[i] > stack[stack.length - 1]) {
      const value = stack.pop();
      mapping[value] = nums2[i];
    }
    stack.push(nums2[i]);
  }
  // now, mapping contains all elements mapped to their next greatest elements, but it might not have every element, because some did not have next greatest elements (they're still in the stack)

  const result = [];

  // iterate over the original list, look up their next greatest elements in the mapping (or get -1 if it doesn't exist)
  for (const num of nums1) {
    if (num in mapping) {
      result.push(mapping[num]);
    } else {
      result.push(-1);
    }
  }

  return result;
};
