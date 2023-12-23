// https://leetcode.com/problems/decode-string/description/
// Difficulty: Medium
// tags: stack

// Problem
/*
Simplified:
Input: s = "3[a2[c]]"
Output: "accaccacc"

Detailed:
Given an encoded string, return its decoded string.

The encoding rule is: k[encoded_string], where the encoded_string inside the square brackets is being repeated exactly k times. Note that k is guaranteed to be a positive integer.

You may assume that the input string is always valid; there are no extra white spaces, square brackets are well-formed, etc. Furthermore, you may assume that the original data does not contain any digits and that digits are only for those repeat numbers, k. For example, there will not be input like 3a or 2[4].

The test cases are generated so that the length of the output will never exceed 105.


 */

// Solution: O(n) space. For time, we do n operations, where the worst case is we handle a ], causing us to do k operations where k is the number of times we have to multiply the string. But as we have nested calls like 2[2[2[a]]], we are doing a larger number of writes / string duplications as the string grows, so the complexity might be O(n*K) where K is all the numbers multiplied together.

/*
Maintain a stack, pushing values, as soon as we encounter a ], pop from the stack to determine the string that needs to be repeated. Then pop from the stack to determine the number of times it should be repeated. Then create the multiplied string and add it to the stack. It is okay if we add it all in one cell, for instance: a[2[b]] -> a bb, now if we tried to multiply this, we would pop off the letters: bb a, reverse them to the original string, a bb, then multiply them together
 */

var decodeString = function (s) {
  const stack = [];

  for (let i = 0; i < s.length; i++) {
    // we have an opening parenthesis, add it to the stack and move on
    if (s[i] === "[") {
      stack.push("[");
    }

    // we have a closing one, handle popping
    else if (s[i] === "]") {
      const letters = [];
      // pop off letters until we reach the opening brace
      while (stack[stack.length - 1] !== "[") {
        const letter = stack.pop();
        letters.push(letter);
      }
      // since the letter were reversed, fix them and form a string
      const string = letters.reverse().join("");
      // remove the [ at the beginning
      stack.pop();

      // now our stack is just a number, pop until we don't get a number
      const numbers = [];
      // keep grabbing numbers as long as they are valid, will also fail when we deplete the entire stack
      while (!isNaN(stack[stack.length - 1])) {
        const num = stack.pop();
        numbers.push(num);
      }
      const repetitions = Number(numbers.reverse().join(""));

      stack.push(string.repeat(repetitions));
    }

    // we have a letter or number, add it to the stack
    else {
      stack.push(s[i]);
    }
  }
  return stack.join("");
};
