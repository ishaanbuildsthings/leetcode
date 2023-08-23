// https://leetcode.com/problems/reorganize-string/description/
// Difficulty: Medium
// Tags: heap

// Problem
/*
Given a string s, rearrange the characters of s so that any two adjacent characters are not the same.

Return any possible rearrangement of s or return "" if not possible.
*/

// Solution, O(n) time and O(n) space
/*
First, get the counts of each char, O(n) time and O(26) space. Then, populate a heap, O(26 log 26) time or O(26) time with heapify.

Then, for n chars, pop from the heap, O(log 26) time. We pop twice to get the two most common, yet different characters, then readd to the heap. Our heap first sorts by frequency, then by alphabetical, to prevent adjacenies. For instance if we have 'ab' as our current result array, then we add 'a' and 'b' back to the heap and they have the same count, prioritize 'a' first. Finally, concatenate the array with takes n time and n space.
*/

class MaxHeap {
  constructor() {
    this.heap = [null];
  }

  compareTuples(tupleA, tupleB) {
    if (tupleA[1] === tupleB[1]) {
      return tupleA[0] < tupleB[0];
    }
    return tupleA[1] < tupleB[1];
  }

  insert(tuple) {
    this.heap.push(tuple);
    let i = this.heap.length - 1;
    while (i > 1) {
      const parent = Math.floor(i / 2);
      if (this.compareTuples(this.heap[parent], this.heap[i])) {
        [this.heap[parent], this.heap[i]] = [this.heap[i], this.heap[parent]];
        i = parent;
      } else {
        break;
      }
    }
  }

  remove() {
    if (this.heap.length === 1) {
      return undefined;
    }

    const result = this.heap[1];
    this.heap[1] = this.heap[this.heap.length - 1];
    this.heap.pop();

    let i = 1;
    while (true) {
      let largest = i;
      const left = 2 * i;
      const right = 2 * i + 1;

      if (
        left < this.heap.length &&
        this.compareTuples(this.heap[largest], this.heap[left])
      ) {
        largest = left;
      }

      if (
        right < this.heap.length &&
        this.compareTuples(this.heap[largest], this.heap[right])
      ) {
        largest = right;
      }

      if (largest !== i) {
        [this.heap[i], this.heap[largest]] = [this.heap[largest], this.heap[i]];
        i = largest;
      } else {
        break;
      }
    }
    return result;
  }

  size() {
    return this.heap.length - 1;
  }

  peek() {
    if (this.heap.length === 1) {
      return undefined;
    }
    return this.heap[1];
  }
}

var reorganizeString = function (s) {
  const heap = new MaxHeap();
  const counts = {};
  for (const char of s) {
    if (!(char in counts)) {
      counts[char] = 1;
    } else {
      counts[char]++;
    }
  }
  for (const key in counts) {
    if (counts[key] > 0) {
      const tuple = [key, counts[key]];
      heap.insert(tuple);
    }
  }

  const resultArr = [];

  while (heap.size() > 0) {
    const first = heap.remove();
    const [char, count] = first;
    if (resultArr[resultArr.length - 1] === char) {
      return "";
    }
    resultArr.push(char);

    if (heap.size() > 0) {
      const second = heap.remove();
      const [char2, count2] = second;
      if (resultArr[resultArr.length - 1] === char2) {
        return "";
      }
      resultArr.push(char2);
      if (count2 > 1) {
        heap.insert([char2, count2 - 1]);
      }
    }

    if (count > 1) {
      heap.insert([char, count - 1]);
    }
  }

  return resultArr.join("");
};
