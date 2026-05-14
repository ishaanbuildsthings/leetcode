// https://leetcode.com/problems/time-based-key-value-store/description/
// Difficulty: Medium
// tags: binary search

// Problem
/*
Simplified: We should be able to add keys with corresponding values, and what time that key was that value: set('tony', 'peng', 1). set('tony', 'bo', 3).
We want to retrieve a value for a key at a certain time: get('tony', 2) -> 'peng', get('tony', 4) -> 'bo', get('tony', 0) -> ''.

Detailed:
Design a time-based key-value data structure that can store multiple values for the same key at different time stamps and retrieve the key's value at a certain timestamp.

Implement the TimeMap class:

TimeMap() Initializes the object of the data structure.
void set(String key, String value, int timestamp) Stores the key key with the value value at the given time timestamp.
String get(String key, int timestamp) Returns a value such that set was called previously, with timestamp_prev <= timestamp. If there are multiple such values, it returns the value associated with the largest timestamp_prev. If there are no values, it returns "".
*/

// Solution: set = O(1) time and space (depending on how we even interpret space), get = O(logn) time, where n is the number of times we have stored that key, O(1) space
/*
 Maintain a data structure that maps keys to a list of tuples, where each tuple contains the time and the value at that time. Since times are only inserted increasingly, we can binary search to retrieve the relevant values.
*/

var TimeMap = function () {
  this.storage = {};
};

/*
  {
    foo : [[3,bar], [4, bar2], [7, baz]],
    ishaan : ____,
    tony : ____,
    }
*/
TimeMap.prototype.set = function (key, value, timestamp) {
  if (key in this.storage) {
    this.storage[key].push([timestamp, value]);
  } else {
    this.storage[key] = [[timestamp, value]];
  }
};

/**
 * @param {string} key
 * @param {number} timestamp
 * @return {string}
 */
TimeMap.prototype.get = function (key, timestamp) {
  if (!(key in this.storage)) {
    return "";
  }

  const timings = this.storage[key];

  let l = 0;
  let r = timings.length - 1;
  let m = Math.floor((r + l) / 2);
  while (l < r) {
    m = Math.floor((r + l) / 2);
    const time = timings[m][0];
    if (time > timestamp) {
      r = m - 1;
    } else if (time === timestamp) {
      return timings[m][1];
    } else if (time < timestamp) {
      l = m + 1;
    }
  }

  if (timings[l][0] > timestamp) {
    l--;
  }

  if (l < 0) {
    return "";
  }

  return timings[l][1];

  // [1, 10] target=5, we see 1, too small, narrow down to [10], bad, we want the value at time 1
  // [5, 10] target=3, we see 5, too big, narrow down to the index before 5, which is good
  // but what if 4 were before the 5? then we would end at time 4, which is still too big for our target, 3. But this isn't possible, if 4 were initially in the array, we could never end at [5, 10]
};

/**
 * Your TimeMap object will be instantiated and called as such:
 * var obj = new TimeMap()
 * obj.set(key,value,timestamp)
 * var param_2 = obj.get(key,timestamp)
 */
