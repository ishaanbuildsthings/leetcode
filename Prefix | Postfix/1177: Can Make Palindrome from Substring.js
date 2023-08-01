// https://leetcode.com/problems/can-make-palindrome-from-substring/description/
// Difficulty: Medium
// tags: prefix

// Problem
/*
You are given a string s and array queries where queries[i] = [lefti, righti, ki]. We may rearrange the substring s[lefti...righti] for each query and then choose up to ki of them to replace with any lowercase English letter.

If the substring is possible to be a palindrome string after the operations above, the result of the query is true. Otherwise, the result is false.

Return a boolean array answer where answer[i] is the result of the ith query queries[i].

Note that each letter is counted individually for replacement, so if, for example s[lefti...righti] = "aaa", and ki = 2, we can only replace two of the letters. Also, note that no query modifies the initial string s.
*/

// Solution, O(s + queries) time, O(s) space
/*
For a given set of letters and k replacements, we need to know if we can make a palindrome. To do so, all even frequency letters are irrelevant. We care about the odd frequency. If we have two odds, we cannot make a palindrome. But if we have two odds and a replacement, we can replace one odd into the other odd, resulting in no odds.

So, set up a range query for the counts of letters. Then, for a range, check up to 26 letters and process the replacements if needed.
*/

var canMakePaliQueries = function (s, queries) {
  const rangeCounts = []; // rangeCounts[i] maps a char count for [:i]
  const counts = {};
  for (let i = 0; i < s.length; i++) {
    const char = s[i];
    if (!(char in counts)) {
      counts[char] = 1;
    } else {
      counts[char]++;
    }
    rangeCounts[i] = JSON.parse(JSON.stringify(counts));
  }
  rangeCounts[-1] = {}; // helps with range query

  function canMakePal(l, r, k) {
    // range query for counts of letters in a region [l:r]
    const rightRangeCount = rangeCounts[r];
    const leftRangeCount = rangeCounts[l - 1];

    const count = {};
    for (const char in rightRangeCount) {
      let resultCount = rightRangeCount[char];
      if (char in leftRangeCount) {
        resultCount -= leftRangeCount[char];
      }
      count[char] = resultCount;
    }

    let changesRemaining = k;

    let oddAllowed = true; // initially we are allowed one odd
    for (const char in count) {
      const freq = count[char];
      // if we have an odd number of letters, but we are allowed to, that is fine
      if (freq % 2 === 1 && oddAllowed) {
        oddAllowed = false;
        continue;
      }
      // if we aren't allowed to have an odd amount, then we can change one of the chars into a previous odd char
      else if (freq % 2 === 1 && !oddAllowed) {
        if (changesRemaining === 0) {
          return false;
        }
        changesRemaining--;
        oddAllowed = true;
      }
    }

    return true;
  }

  const result = [];

  for (const [left, right, k] of queries) {
    const bool = canMakePal(left, right, k);
    result.push(bool);
  }

  return result;
};
