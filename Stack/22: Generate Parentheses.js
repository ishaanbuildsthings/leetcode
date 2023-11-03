// https://leetcode.com/problems/generate-parentheses/description/
// Difficulty: Medium
// tags: recursion, backtracking, stack

// Problem
/*
Simfplied: n=3, return ["((()))","(()())","(())()","()(())","()()()"]
Detailed:
Given n pairs of parentheses, write a function to generate all combinations of well-formed parentheses.
*/

// Solution: Time: O(n* 2^2n) upper bound as we have at most 2 choices per position, and there is at most depth 2n chains. Memory is O(n) as the depth of the callstack is 2n, and the stck is also 2n. We serialize 2^n options also.
/*
We use a backtracking solution to simulate all possible valid arrangements of parentheses, and when we reach our base case we add it to the results. We use a stack to add and remove parentheses from. We could also makae the recurse function accept a string parameter and modify the string, but this creates a lot of string duplication under the hood, since the strings are immutable.

When we add a parenthesis, we can always add an opening one, as long as we haven't used all of them yet. For instance n=3, after ((( we can't add more. But what about ()())? We can't add an opening one since it would terminate the loop and form an invalid sequence. We handle this by never adding a closing parenthesis unless there is at least one opening one to accompany it. Technically we can remove a lot of conditions from the code below, but I have left them in to make it more clear what is going on, though they are redundant.
*/

var generateParenthesis = function (n) {
  const results = [];
  const stack = [];

  function recurse(leftUsed, rightUsed) {
    if (leftUsed === n && rightUsed === n) {
      results.push(stack.join(""));
    }
    // we can always add a left parenthesis if we have enough right ones to close all the open lefts
    const rightsAvailable = n - rightUsed;
    if (leftUsed < n && rightsAvailable > leftUsed - rightUsed) {
      stack.push("(");
      recurse(leftUsed + 1, rightUsed);
      stack.pop();
    }

    // we can always add a right parenthesis if it closes an open left one
    if (rightUsed < n && rightUsed < leftUsed) {
      stack.push(")");
      recurse(leftUsed, rightUsed + 1);
      stack.pop();
    }
  }

  recurse(0, 0);
  return results;
};
