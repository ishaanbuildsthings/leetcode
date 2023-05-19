// https://leetcode.com/problems/remove-k-digits/description/
// Difficulty: Medium
// tags: monotonic stack

// Problem
/*
Given string num representing a non-negative integer num, and an integer k, return the smallest possible integer after removing k digits from num.
Input: num = "10200", k = 1
Output: "200"
Explanation: Remove the leading 1 and the number is 200. Note that the output must not contain leading zeroes.
*/

// Solution:
/*
Add numbers to the stack, as soon as we see a smaller number, we would prefer to drop the prefix in exchange for that. For instance we have a 3, and we get a 2, it's better to pop the 3 off and add the 2, to minimize the prefix. We keep doing this until our stack is once again monotonically increasing or we run out of changes we can make. If we finish and we still have changes left, say our stack is 1 2 3, then we start to pop from the end as we don't want to remove our small prefixes. Also handle the edge case where we have leading 0s.
At most, we can add n elements to the stack, and remove n elements to the stack. Our time is O(n). Our space is also O(n), since at most we could concurrently hold n elements in the stack, even though the output is smaller.
In solution 2, instead of duplicating a stack to remove the initial 0s, we just never add 0s to an empty stack to begin with, making the calculation fewer cycles.
*/
var removeKdigits = function (num, k) {
  let counter = k; // indicates how many more removals we have left

  // if we can remove every digit, like '10' k=2, return '0' as opposed to a blank string
  if (k === num.length) {
    return "0";
  }

  const stack = [num[0]]; // prevent edge case where we don't have a prior number to compare to
  for (let i = 1; i < num.length; i++) {
    // if our new number is smaller, and we have changes left, we can bump out the old bigger prefix for the new one
    if (num[i] < stack[stack.length - 1] && counter > 0) {
      while (stack[stack.length - 1] > num[i] && counter > 0) {
        stack.pop();
        counter--;
      }
    }
    // if our new number was a 0 and our stack is empty, don't add it
    if (stack.length === 0 && num[i] === "0") {
      continue;
    }
    stack.push(num[i]);
  }

  // if we have leftover removals, pop from the back, since our stack is monotonically increasing, 1234 optimal is always to remove from the right since we don't want to remove our smaller prefixes compared to the larger ending
  while (counter > 0) {
    stack.pop();
    counter--;
  }

  // since we never added 0s, handle edge case
  if (stack.length === 0) {
    return "0";
  }

  return stack.join("");
};
