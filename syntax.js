// getting elements from an array (destructuring)
const arr = [1, 2, 3, 4, 5];

const [zero, first] = arr; // gets 1 and 2

const [second, third, fourth] = arr.slice(2, 5); // gets the 2nd to 4th, not including 4th elements
// or
const [second, third, fourth] = arr.slice(2);


// modifying an array in place
const arr = [1, 2, 3, 4, 5];

arr.splice(index, how many elements):

arr.splice(2, 2); // removes 3 and 4


// creating an empty array
const arr = new Array(5); // creates an array of length 5 filled with undefined
const arr = new Array(5).fill(3); // creates an array of length 5 filled with 3s


// hash sets
const set = new Set();
set.add(1);
set.has(3);


// reduce
const arr = [1, 2, 3, 4, 5];
const sum = arr.reduce((acc, value) => acc + value, 0); // 15

// absolute value
Math.abs(...)

