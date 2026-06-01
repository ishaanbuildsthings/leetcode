// https://leetcode.com/problems/group-shifted-strings/description/
// difficulty: Medium

// Problem
/*
We can shift a string by shifting each of its letters to its successive letter.

For example, "abc" can be shifted to be "bcd".
We can keep shifting the string to form a sequence.

For example, we can keep shifting "abc" to form the sequence: "abc" -> "bcd" -> ... -> "xyz".
Given an array of strings strings, group all strings[i] that belong to the same shifting sequence. You may return the answer in any order.
*/

// Solution, O(words * letters) time and O(words) space
/*
To tell if two words take the same form, we can essentially emulate if we shifted the first letter down to 'a'. Instead of actually doing that, I did it with numbers / charcodes instead. So for each word, for each letter, compute the shifted version. I also store these 'base' shifted versions, where the first letter is pegged at a, in a hashmap, to buckets of grouped letters. This requires at most n space. I also had to do a +26 trick which can be seen in the comments.
*/

var groupStrings = function (strings) {
  const groupings = {}; // maps a 0-set (by the first letter) grouping to a list of words it includes
  for (const word of strings) {
    const numConversion = []; // if the word is bac, we 0-set based on b, and therefore the output is 0, -1, 1, essentially the distance from the first char

    const firstCharNum = word[0].charCodeAt(0);
    for (const char of word) {
      let code = char.charCodeAt(0) - firstCharNum;
      // this is for situations where 'az' and 'ba', don't get grouped together, in the first, z is considered higher than a, in the second, a is considered lower than b, so we let it wrap around back to b with the +26
      if (code < 0) {
        code += 26;
      }
      numConversion.push(code);
    }

    const key = JSON.stringify(numConversion);

    if (key in groupings) {
      groupings[key].push(word);
    } else {
      groupings[key] = [word];
    }
  }

  const result = [];
  for (const key in groupings) {
    result.push(groupings[key]);
  }

  return result;
};
