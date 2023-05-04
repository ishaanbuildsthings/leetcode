// https://leetcode.com/problems/longest-turbulent-subarray/description/
// Difficulty: Medium
// tags: sliding window variable, kadane's (sort of)

// Solution
// O(n) time and O(1) space
// Iterate over the array, maintaining a prefix for the previous sign. For instance [6, 8, 7], at 7 our prefix sign was '>', and our current sign is '<'. Based on those two signs, update the dpSize

const maxTurbulenceSize = function (arr) {
  let prefixSign = "=";
  let maxSize = 1;
  let dpSize = 1;
  for (let i = 1; i < arr.length; i++) {
    // create sign
    let sign;
    if (arr[i] === arr[i - 1]) {
      sign = "=";
    } else if (arr[i] > arr[i - 1]) {
      sign = ">";
    } else {
      sign = "<";
    }

    if (sign === "=") {
      prefixSign = "=";
      dpSize = 1;
    } else if (sign === prefixSign) {
      dpSize = 2;
    } else {
      prefixSign = sign;
      dpSize++;
    }
    maxSize = Math.max(maxSize, dpSize);
  }
  return maxSize;
};

// Same solution, just more wordy

const maxTurbulenceSize2 = function (arr) {
  let lastDirection = "either";
  let maxSize = 1;
  let dpSize = 1;
  for (let i = 1; i < arr.length; i++) {
    if (lastDirection === "either") {
      if (arr[i] > arr[i - 1]) {
        lastDirection = "up";
        dpSize++;
      } else if (arr[i] < arr[i - 1]) {
        lastDirection = "down";
        dpSize++;
      }
    } else if (lastDirection === "up") {
      if (arr[i] > arr[i - 1]) {
        lastDirection = "up";
        dpSize = 2;
      } else if (arr[i] < arr[i - 1]) {
        lastDirection = "down";
        dpSize++;
      }
    } else if (lastDirection === "down") {
      if (arr[i] > arr[i - 1]) {
        lastDirection = "up";
        dpSize++;
      } else if (arr[i] < arr[i - 1]) {
        lastDirection = "down";
        dpSize = 2;
      }
    }
    if (arr[i] === arr[i - 1]) {
      lastDirection = "either";
      dpSize = 1;
    }
    maxSize = Math.max(maxSize, dpSize);
  }
  return maxSize;
};
