// https://leetcode.com/problems/inversion-of-object/submissions/1099560168/
// difficulty: easy

// Problem
// Given an object or an array obj, return an inverted object or array invertedObj.

// The invertedObj should have the keys of obj as values and the values of obj as keys. The indices of array should be treated as keys. It is guaranteed that the values in obj are only strings. The function should handle duplicates, meaning that if there are multiple keys in obj with the same value, the invertedObj should map the value to an array containing all corresponding keys.

// Solution
// There are many ways to solve this. First, a non-functional way:

var invertObject = function (obj) {
  const inverted = {};
  for (const key in obj) {
    const invertedKey = obj[key];
    const newInvertedVal = key;
    if (invertedKey in inverted) {
      if (Array.isArray(inverted[invertedKey])) {
        inverted[invertedKey].push(newInvertedVal);
      } else {
        inverted[invertedKey] = [inverted[invertedKey], newInvertedVal];
      }
    } else {
      inverted[invertedKey] = newInvertedVal;
    }
  }
  return inverted;
};

// Second, a functional but inefficient way due to the .concat time complexity
var invertObject = function (obj) {
  return Object.entries(obj).reduce((accumulated, [key, value]) => {
    accumulated[value] = accumulated[value]
      ? [].concat(accumulated[value], key)
      : key;
    return accumulated;
  }, {});
};

// Third, a functional but efficient way:
var invertObject = function (obj) {
  // accumulated will be the object or the initial value on the first run
  // each call to the reducer returns a new object which is passed as the accumulator again
  return Object.entries(obj).reduce((accumulated, [key, value]) => {
    if (Array.isArray(accumulated[value])) {
      accumulated[value].push(key);
    } else if (accumulated[value] !== undefined) {
      accumulated[value] = [accumulated[value], key];
    } else {
      accumulated[value] = key;
    }
    return accumulated;
  }, {});
};
