// https://leetcode.com/problems/decode-string/description/
// Difficulty: Medium
// tags: stack

// Problem
/*
 */

// Solution: O(n) space, not sure about time is it complex

/*
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
