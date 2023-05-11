// https://leetcode.com/problems/maximum-number-of-balloons/description/
// Difficulty: Easy

// Problem
/*
Simple explanation: Given a string text, you want to use the characters of text to form as many instances of the word "balloon" as possible. Each character can be used only once.
*/

// Solution
// O(n) time and O(1) space (since the mapping for balloon is constant) Iterate over the string and count the number of times each character appears. Then, iterate over the count, and assess the bottleneck character.

var maxNumberOfBalloons = function (text) {
  const count = { b: 0, a: 0, l: 0, o: 0, n: 0 };
  for (const char of text) {
    if (char in count) {
      count[char]++;
    }
  }

  // intialize this to be the count of any letter, if we make it 0, then our max possible balloons will always be set to 0 since that is <= the count of the letter
  let maxPossibleBalloons = count.b;

  for (const key in count) {
    if (key === "b" || key === "a" || key === "n") {
      maxPossibleBalloons = Math.min(maxPossibleBalloons, count[key]);
    } else {
      maxPossibleBalloons = Math.min(
        maxPossibleBalloons,
        Math.floor(count[key] / 2)
      );
    }
  }

  return maxPossibleBalloons;
};
