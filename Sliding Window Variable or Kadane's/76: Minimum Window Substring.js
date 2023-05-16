// https://leetcode.com/problems/minimum-window-substring/description/
// Difficulty: Hard
// tags: sliding window variable

// Problem
/*
Given two strings s and t of lengths m and n respectively, return the minimum window substring of s such that every character in t (including duplicates) is included in the window. If there is no such substring, return the empty string "".

The testcases will be generated such that the answer is unique.
*/

// Solution 1
/*
Similar to solution 2, but with some optimizations. When we add a letter we need, for instance our target is ABC and we reach AEEB, adding a B we need, we have to check all the characters. We don't have a way to know if we have enough A's already, enough C's, etc. We can know if we already had enough B's we could skip that, but that's a different optimization. What we should do is keep a count for how many letter types we still need more of, for instance after AEEB we need only 1 more, which is to fulfill the Cs. We know this because we have 2 fulfilled, and we needed 3 fulfilled overall. Any time we reach a letter, if we fulfill it we update our fulfill count. Anytime if we decrement a letter and we dip below the needed amount for that, we remove 1 from our had count. When our haveCount===needCount, we know we have a valid substring. This is better because instead of iterating through each letter to check if we fulfilled those, we just keep a count of how many we have. And we know if we fulfill a new one for the first time, it wasn't counted before, and must go up.
*/
// *** SEE SOLUTION 2 AND 3 WRITEUPS ***

const LETTERS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ";
const template = {};
for (const letter of LETTERS) {
  template[letter] = 0;
}
var minWindow = function (string, target) {
  // create the targetMapping
  const targetMapping = {};
  for (const char of target) {
    if (!targetMapping[char]) {
      targetMapping[char] = 1;
    } else {
      targetMapping[char]++;
    }
  }

  let l = 0;
  let r = 0;
  let haveCount = 0;
  let needCount = Object.keys(targetMapping).length;
  let optimalL = 0;
  let optimalR = Infinity;
  const windowMapping = { ...template };

  while (r < string.length) {
    const char = string[r];
    windowMapping[char]++;

    // skip characters that won't make our window desirable (we already have them) because we have enough of those already
    if (windowMapping[char] > targetMapping[char]) {
      r++;
      continue;
    }
    // skip characters that won't make our window desirable because they aren't in the target
    if (!(char in targetMapping)) {
      r++;
      continue;
    }

    // check if we have exactly enough of this character, adding to our haveCount since we didn't have it before
    if (windowMapping[char] === targetMapping[char]) {
      haveCount++;
    }

    // desirable
    while (haveCount === needCount) {
      // if we have the shortest substring, update that
      if (r - l + 1 < optimalR - optimalL + 1) {
        optimalL = l;
        optimalR = r;
      }
      // remove the character
      windowMapping[string[l]]--;
      l++;
      // check if that made it undesirable
      if (windowMapping[string[l - 1]] === targetMapping[string[l - 1]] - 1) {
        haveCount--;
        break;
      }
    }
    r++;
  }

  // we never found a minimum substring
  if (optimalR === Infinity) {
    return "";
  }

  return string.slice(optimalL, optimalR + 1);
};

// *** SEE SOLUTION 1 AND 3 WRITEUPS ***

// Solution 2
// Same as solution 3, but using pointers instead of lots of .slice. Also added a condition to skip characters that aren't in the target at all. They can be ignored, because they would never make the window desirable. It doesn't matter if we decrement those from the windowMapping when we delete them from the left (they would become negative since we never added them) since we never use those values anyway. Also added an optimization that when we decrement from the left, we only check if decrementing that character made our window undesirable, since we were desirable before.

const LETTERS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ";
const template = {};
for (const letter of LETTERS) {
  template[letter] = 0;
}
var minWindow = function (string, target) {
  // create the targetMapping
  const targetMapping = {};
  for (const char of target) {
    if (!targetMapping[char]) {
      targetMapping[char] = 1;
    } else {
      targetMapping[char]++;
    }
  }

  let l = 0;
  let r = 0;
  let optimalL = 0;
  let optimalR = Infinity;
  const windowMapping = { ...template };

  while (r < string.length) {
    const char = string[r];
    windowMapping[char]++;

    // skip characters that won't make our window desirable because we have enough of those
    if (windowMapping[char] > targetMapping[char]) {
      r++;
      continue;
    }
    // skip characters that won't make our window desirable because they aren't in the target
    if (!(char in targetMapping)) {
      r++;
      continue;
    }

    // check if the window mapping is desirable via the missingCharacter variable, assign it to a boolean since it's a complex task and cannot be captured in a condition inside a while loop
    let missingCharacter = false;
    for (const char in targetMapping) {
      if (windowMapping[char] < targetMapping[char]) {
        missingCharacter = true;
        break;
      }
    }

    // while we are desirable, update the minimumSubstring, decrement from the left, and update the desirability
    while (!missingCharacter) {
      // if we have the shortest substring, update that
      if (r - l + 1 < optimalR - optimalL + 1) {
        optimalL = l;
        optimalR = r;
      }
      // decrement the left character
      windowMapping[string[l]]--;
      l++;
      // if the left character amount dropped below what was needed, we are no longer desirable. If the character we dropped wasn't in the target, we would get a number < undefined in the conditional which would still be false, which is good.
      if (windowMapping[string[l - 1]] < targetMapping[string[l - 1]]) {
        missingCharacter = true;
      }
    }
    r++;
  }

  // we never found a minimum substring
  if (optimalR === Infinity) {
    return "";
  }

  return string.slice(optimalL, optimalR + 1);
};

// Solution 3
// *** SEE SOLUTION 1 AND 2 WRITEUPS ***
// O(n+m) time, I think. n is the length of the string, m is the length of the target. Technically we can also say the time complexity is O(n) since if the length of the target is > the length of the string we can immediately return an empty string. As for the n part of the time complexity, I believe it is linear. We iterate over the string n times. The only operation inside the loop I am unsure of is when we do string.slice(...). string.slice(l, r) itself is an r-l computation, but I don't see a way to guarantee that the values of r-l will be linear. It comes down to how often we need to update the minimum substring. A trivial improvement would be to use pointers to track the location of the substring boundaries, and compute the substring only once at the end, which would definitely make the complexity linear. The space storage is O(1) since letter mappings are fixed in size.

// Create a target mapping. Iterate over the string, adding characters. If we already have too many of that character, we know this new character won't make our window valid, so continue. If we see a new character, add it, and check if we are desirable. If not, continue the while loop. If we are desirable, update the minimum substring, and decrement from the left until we aren't desirable, updating each time.
/*
A strange case may be: AEECEEBCA and our target is ABC
Our first desirable window is A...BC. When we decrement from the left, we drop the A, which makes our window undesirable. But we can keep decrementing technically, since removing extra characters like the C, or unrelated characters like the E won't add further issues to our window. But we don't need to do this. This is because the next time our window is desirable, on the last A, we will decrement from the left continuously until it isn't, and we would drop those extra characters then. If the last character of the window specifically makes it desirable, then when we decrement from the left and make it undesirable, we don't care about decrementing more letters like the E or first C, because we would have no more characters to make the window desirable again anyway.
*/

const LETTERS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ";
const template = {};
for (const letter of LETTERS) {
  template[letter] = 0;
}

var minWindow = function (string, target) {
  // create the targetMapping
  const targetMapping = {};
  for (const char of target) {
    if (!targetMapping[char]) {
      targetMapping[char] = 1;
    } else {
      targetMapping[char]++;
    }
  }

  // kind of jank way to check if the minimum substring is the default value, there are other ways too, such as counting how many times it has changed. We can't just assign it to be the string, because if the string itself doesn't have all the characters, we should return a blank string. But it's also possible the string itself is indeed the minimum substring.
  let minimumSubstring = string + "a";
  let l = 0;
  let r = 0;
  const windowMapping = { ...template };

  while (r < string.length) {
    const char = string[r];
    windowMapping[char]++;

    if (windowMapping[char] > targetMapping[char]) {
      r++;
      continue;
    }

    // check if the window mapping is desirable via the missingCharacter variable, assign it to a boolean since it's a complex task and cannot be captured in a condition inside a while loop
    let missingCharacter = false;
    for (const char in targetMapping) {
      if (windowMapping[char] < targetMapping[char]) {
        missingCharacter = true;
        break;
      }
    }

    // while we are desirable, update the minimumSubstring, decrement from the left, and update the desirability
    while (!missingCharacter) {
      if (r - l + 1 < minimumSubstring.length) {
        minimumSubstring = string.slice(l, r + 1);
      }
      windowMapping[string[l]]--;
      l++;

      for (const key in targetMapping) {
        if (windowMapping[key] < targetMapping[key]) {
          missingCharacter = true;
          break;
        }
      }
    }
    r++;
  }

  if (minimumSubstring === string + "a") return "";
  return minimumSubstring;
};
