// getting elements from an array (destructuring)
const arr = [1, 2, 3, 4, 5];

const [zero, first] = arr; // gets 1 and 2

const [second, third, fourth] = arr.slice(2, 5); // gets the 2nd to 4th, not including 4th elements
// or
const [second, third, fourth] = arr.slice(2);



// modifying an array in place
const arr = [1, 2, 3, 4, 5];

arr.splice(index, how many elements to remove including that index):

arr.splice(2, 2); // removes 3 and 4
arr.splice(2, 1, 5); // removes 3 and adds 5
arr.splice(2, 0, 5); // adds the 5 so its now index 2


// creating an array
const arr = new Array(5); // creates a sparse array of length 5
const arr = new Array(5).fill(3); // creates an array of length 5 filled with 3s
const arr = new Array(5).fill(); // fills it with undefined

DO NOT FILL AN ARRAY WITH[] or { } because it will fill it with references to the same object

instead you could do:

  const arr = new Array(5).fill().map(() => []); // creates an array of length 5 filled with empty arrays

  this incurs a memory performance overhead, since .map creates a copy,

const str = 'how are you?';
const arr = str.split(' '); // ['how', 'are', 'you?']


// hash sets
const set = new Set();
set.add(1);
set.has(3);
set.delete(3);
set.size; // returns length
const arr = [1, 2, 3];
const set = new Set(arr); // creates a set from an array

// map
const arr2 = arr.map((value, index) => ...); // we can access index as well, useful for things like sorting two arrays based on one
const positions = [1, 5, 3, 2];
const speeds = [9, 2, 4, 6];
const tuples = positions.map((pos, i) => [pos, speeds[i]]); // [[1, 9], [5, 2], [3, 4], [2, 6]]


// reduce
const arr = [1, 2, 3, 4, 5];
const sum = arr.reduce((acc, value) => acc + value, 0); // 15

// strings
let str = 'hello';
str.slice(1, 3); // 'el', incudes index but not suffix
str.slice(1); // 'ello', goes until end
str[5] = 'x'; but cannot be reassigned in place in the string
const arr = ['a', 'b', 'c'];
const str = arr.join(''); // 'abc'
const str2 = arr.join(' '); // 'a b c'
'hi'.repeat(5) // 'hihihihihi'
// checking if a string is a valid number
isNaN('hi'); // true
isNaN('1'); // false

// types
typeof 1; // 'number'

// absolute value
Math.abs(...)

// floor / ceiling
Math.floor(number)
Math.ceil(number)

// infinity
const x = Number.POSITIVE_INFINITY;
const y = Number.NEGATIVE_INFINITY;

// map
const a = b.map((element, index) => ...);
// handling matrices
trying to iterate over a matrix and process columns, use a .map:
for (let colNumber = 0; colNumber < matrix[0].length; colNumber++) {
  const column = matrix.map(row => row[colNumber]);
  // process the column
}

// you can also make sure the matrix isnt rotated like this:

const matrix = [
  [1, 2, 3],
  [4, 5, 6],
  [7, 8, 9]
];

const numRows = matrix.length;
const numCols = matrix[0].length;
const resultMatrix = new Array(numRows).fill(0).map(() => new Array(numCols).fill(0));

for (let colNumber = 0; colNumber < numCols; colNumber++) {
  const column = matrix.map(row => row[colNumber] * 2); // extract the data and process the column

  for (let rowNumber = 0; rowNumber < numRows; rowNumber++) {
    resultMatrix[rowNumber][colNumber] = column[rowNumber];
  }
}

// deleting a key
delete obj.key;
delete obj[variableName];

// sorting
arr.sort((a, b) => a - b);
if < 0, a goes before b, if 0, order perserved, if > 0, b goes before a

// maps, useful for using objects as keys
const myMap = new Map();
myMap.set(key, value);
myMap.get(key);