// https://leetcode.com/problems/create-object-from-two-arrays/description/
// difficulty: easy

/*
Problem
Given two arrays keysArr and valuesArr, return a new object obj. Each key-value pair in obj should come from keysArr[i] and valuesArr[i].

If a duplicate key exists at a previous index, that key-value should be excluded. In other words, only the first key should be added to the object.

If the key is not a string, it should be converted into a string by calling String() on it.
*/

// Solution, standard linear creation

/**
 * @param {Array} keysArr
 * @param {Array} valuesArr
 * @return {Object}
 */
var createObject = function (keysArr, valuesArr) {
  const res = {};
  for (let i = 0; i < keysArr.length; i++) {
    if (keysArr[i] in res) {
      continue;
    }
    res[keysArr[i]] = valuesArr[i];
  }
  return res;
};
