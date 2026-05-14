// https://leetcode.com/problems/design-hashset/description/
// Difficulty: Easy

// Problem
/*
Design a HashSet without using any built-in hash table libraries.

Implement MyHashSet class:

void add(key) Inserts the value key into the HashSet.
bool contains(key) Returns whether the value key exists in the HashSet or not.
void remove(key) Removes the value key in the HashSet. If key does not exist in the HashSet, do nothing.
*/

// Solution, O(1) time to add a key and O(1) time to remove a key, given few collisions. O(1) time to check if a key exists. O(n) space for the underlying array, or you could consider it O(1) if we don't count the space the hashset needs itself. Though at any given point, with the current implementation, we fill the underlying storage with arrays even when there are no values, so there is memory allocated always.

/*
Maintain an underlying array and a size variable. When we add a value, hash it, check the bucket it hashed to, to see if it existed already, otherwise add it. Resize as needed. When deleting an element, search the bucket and do a splice operation. Can use a linked list to have O(1) removal but it shouldn't matter much given the resizing anyway.
*/

var MyHashSet = function () {
  this.storage = new Array(8).fill().map(() => []); // contains buckets
  this.sizeMax = 8; // indicates the max storage size
  this.size = 0; // indicates number of values current stored
  this.MAX_FACTOR = 0.75;
  this.MIN_FACTOR = 0.25;
};

MyHashSet.prototype.hash = function (key) {
  const hashedIndex = key % this.sizeMax;
  return hashedIndex;
};

MyHashSet.prototype.add = function (key) {
  // check if the element exists
  const hashedIndex = this.hash(key); // produces 0 to this.sizeMax-1
  const bucket = this.storage[hashedIndex];
  for (const value of bucket) {
    if (value === key) {
      return;
    }
  }
  this.storage[hashedIndex].push(key);

  this.size++;

  // resize if too many elements
  if (this.size >= this.MAX_FACTOR * this.sizeMax) {
    this.sizeMax *= 2;
    const newStorage = new Array(this.sizeMax).fill().map(() => []);
    for (const bucket of this.storage) {
      for (const element of bucket) {
        const hashedIndexNewStorage = this.hash(element);
        newStorage[hashedIndexNewStorage].push(element);
      }
    }
    this.storage = newStorage;
  }
};

MyHashSet.prototype.remove = function (key) {
  const hashedIndex = this.hash(key);

  for (let i = 0; i < this.storage[hashedIndex].length; i++) {
    const element = this.storage[hashedIndex][i];
    if (element === key) {
      this.storage[hashedIndex].splice(i, 1);
      this.size--;
      break;
    }
  }

  // resize if too few elements
  if (this.size < this.MIN_FACTOR * this.sizeMax) {
    this.sizeMax /= 2;
    const newStorage = new Array(this.sizeMax).fill().map(() => []);
    for (const bucket of this.storage) {
      for (const element of bucket) {
        const hashedIndexNewStorage = this.hash(element);
        newStorage[hashedIndexNewStorage].push(element);
      }
    }
    this.storage = newStorage;
  }
};

MyHashSet.prototype.contains = function (key) {
  const hashedIndex = this.hash(key);
  const bucket = this.storage[hashedIndex];
  for (const element of bucket) {
    if (element === key) {
      return true;
    }
  }
  return false;
};

/**
 * Your MyHashSet object will be instantiated and called as such:
 * var obj = new MyHashSet()
 * obj.add(key)
 * obj.remove(key)
 * var param_3 = obj.contains(key)
 */
