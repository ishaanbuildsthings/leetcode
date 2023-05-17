// https://leetcode.com/problems/design-hashmap/description/
// Difficulty: Easy

// Problem
/*
Design a HashMap without using any built-in hash table libraries.

Implement the MyHashMap class:

MyHashMap() initializes the object with an empty map.
void put(int key, int value) inserts a (key, value) pair into the HashMap. If the key already exists in the map, update the corresponding value.
int get(int key) returns the value to which the specified key is mapped, or -1 if this map contains no mapping for the key.
void remove(key) removes the key and its corresponding value if the map contains the mapping for the key.
*/

// Solution
/*
To implement a hash-map, we can use linear probing (ideally with tombstones and increased step sizes), or separate chaining. For this problem, separate chaining is easier to implement. We intialize some storage and constants that indicate when to double or halve our underlying array size. Since our array is dynamic, we just treat the hash function to only hash within some predefined size (the length of the storage). To add a location, we hash the key with a modulo, check the hashed position, and add the element / push it to the bucket. To retrieve it, we do the same thing, iterating over the buckets and comparing the keys.
*/

const DOUBLE_FACTOR = 0.75;
const HALF_FACTOR = 0.25;

var MyHashMap = function () {
  this.totalPairs = 0;
  this.storage = new Array(4).fill().map(() => []); // will look like: [ [ [0, 10], [4, 5] ], [], [], [] ]
};

MyHashMap.prototype.put = function (key, value) {
  const insertLocation = key % this.storage.length;
  const bucket = this.storage[insertLocation];
  let editedPair = false;
  for (let i = 0; i < bucket.length; i++) {
    const pair = bucket[i];
    if (pair[0] === key) {
      pair[1] = value;
      editedPair = true;
      break;
    }
  }

  if (!editedPair) {
    this.storage[insertLocation].push([key, value]);
    this.totalPairs++;
  }

  // double the array and rehash the elemnets
  if (this.totalPairs / this.storage.length > DOUBLE_FACTOR) {
    // create the new array, an O(n) operation
    const newStorage = new Array(this.storage.length * 2).fill().map(() => []);
    // iterate over every bucket from the first array
    for (const bucket of this.storage) {
      // for every bucket, add new key:value pairs to the new storage
      for (const pair of bucket) {
        const key = pair[0];
        const insertLocation = key % newStorage.length;
        const value = pair[1];
        newStorage[insertLocation].push([key, value]);
      }
    }
    this.storage = newStorage;
  }
};

MyHashMap.prototype.get = function (key) {
  const hashIndex = key % this.storage.length;
  const bucket = this.storage[hashIndex];
  for (const pair of bucket) {
    if (pair[0] === key) {
      return pair[1];
    }
  }
  return -1;
};

MyHashMap.prototype.remove = function (key) {
  const hashIndex = key % this.storage.length;
  const bucket = this.storage[hashIndex];
  for (let i = 0; i < bucket.length; i++) {
    if (bucket[i][0] === key) {
      bucket.splice(i, 1);
      this.totalPairs--;
      break;
    }
  }

  if (this.totalPairs < this.storage.length * HALF_FACTOR) {
    const newStorage = new Array(this.storage.length / 2).fill().map(() => []);
    // iterate over every bucket from the first array
    for (const bucket of this.storage) {
      // for every bucket, add new key:value pairs to the new storage
      for (const pair of bucket) {
        const key = pair[0];
        const insertLocation = key % newStorage.length;
        const value = pair[1];
        newStorage[insertLocation].push([key, value]);
      }
    }
    this.storage = newStorage;
  }
};

/**
 * Your MyHashMap object will be instantiated and called as such:
 * var obj = new MyHashMap()
 * obj.put(key,value)
 * var param_2 = obj.get(key)
 * obj.remove(key)
 */
