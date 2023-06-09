// https://leetcode.com/problems/permutations/description/

// Solution 1, adding number of neighbor and popping it
// time: O(n * n!), there are n! possible permutations and each one takes n time to serialize. Each one also takes n time to iterate possible continuations. Our space complexity is O(n) due to the recursive callstack. Complexities are listed assuming a set is used.
/*
Maintain a list of current numbers we have seen. Call all valid numbers. Do this by adding the number to the stack, calling it, then popping.

Both solution 1 and solution 2 can be improved by using a set for lookup speed.
*/
var permute = function (nums) {
  const result = [];

  function backtrack(currentNums) {
    // if we have exactly enough numbers, we have a result
    if (currentNums.length === nums.length) {
      result.push(JSON.parse(JSON.stringify(currentNums)));
      return;
    }
    /* here we don't have enough numbers */

    for (const num of nums) {
      // skip numbers we have already used
      if (currentNums.includes(num)) continue;
      currentNums.push(num);
      backtrack(currentNums);
      currentNums.pop();
    }
  }

  backtrack([]);

  return result;
};

// Solution 2, adding number when visited, same complexities as solution 1
/*
Maintain a list of the current numbers we have. Our function also accepts the number we were called with. Once called, we add that number to our stack. We recurse on all valid neighbors, then pop our number.
*/
var permute = function (nums) {
  const result = [];

  function backtrack(currentNums, num) {
    currentNums.push(num);
    // if we have exactly enough numbers, we have a result
    if (currentNums.length === nums.length) {
      result.push(JSON.parse(JSON.stringify(currentNums)));
      currentNums.pop();
      return;
    }
    /* here we don't have enough numbers */

    for (const num of nums) {
      // skip numbers we have already used
      if (currentNums.includes(num)) continue;
      backtrack(currentNums, num);
    }

    currentNums.pop();
  }

  for (const num of nums) {
    backtrack([], num);
  }

  return result;
};
