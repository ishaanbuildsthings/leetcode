// https://leetcode.com/problems/dota2-senate/description/
// Difficulty: Medium
// tags: recursion

const predictPartyVictory = function (senate) {
  const occurences = { R: 0, D: 0 };

  for (const char of senate) {
    occurences[char]++;
  }

  function recurse(string, turnIndex) {
    if (turnIndex >= string.length) {
      turnIndex = 0;
    }
    // base case
    if (
      (occurences["R"] > 0 && occurences["D"] === 0) ||
      (occurences["D"] > 0 && occurences["R"] === 0)
    ) {
      return string[0] === "R" ? "Radiant" : "Dire";
    }

    // check for peoples turns after
    for (let i = turnIndex + 1; i < string.length; i++) {
      // found an opposite voter
      if (string[i] !== string[turnIndex]) {
        occurences[string[i]]--;
        string = string.slice(0, i) + string.slice(i + 1);
        return recurse(string, turnIndex + 1);
      }
    }
    // check for peoples turns from the beginning
    for (let i = 0; i < string.length; i++) {
      if (string[i] !== string[turnIndex]) {
        occurences[string[i]]--;
        string = string.slice(0, i) + string.slice(i + 1);
        return recurse(string, turnIndex);
      }
    }
  }
  return recurse(senate, 0);
};
