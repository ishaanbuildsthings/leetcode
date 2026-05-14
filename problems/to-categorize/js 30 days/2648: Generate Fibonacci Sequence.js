// https://leetcode.com/problems/generate-fibonacci-sequence/description/
// difficulty: easy

/*
Problem

Write a generator function that returns a generator object which yields the fibonacci sequence.

The fibonacci sequence is defined by the relation Xn = Xn-1 + Xn-2.

The first few numbers of the series are 0, 1, 1, 2, 3, 5, 8, 13.
*/

// Solution, initially I had hard coded yield 0 and yield 1 but we can just yield prevPrev

/**
 * @return {Generator<number>}
 */
var fibGenerator = function* () {
  let prevPrev = 0;
  let prev = 1;
  while (true) {
    yield prevPrev;
    const newFib = prevPrev + prev;
    prevPrev = prev;
    prev = newFib;
  }
};

/**
 * const gen = fibGenerator();
 * gen.next().value; // 0
 * gen.next().value; // 1
 */
