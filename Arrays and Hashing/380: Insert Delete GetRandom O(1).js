// leetcode.com/problems/insert-delete-getrandom-o1/description/
// Difficulty: Medium

// Problem
/*
Simplified: Create a set object with O(1) insert, O(1) remove, and O(1) get random that gives equal chances for all elements.

Detailed:
Implement the RandomizedSet class:

RandomizedSet() Initializes the RandomizedSet object.
bool insert(int val) Inserts an item val into the set if not present. Returns true if the item was not present, false otherwise.
bool remove(int val) Removes an item val from the set if present. Returns true if the item was present, false otherwise.
int getRandom() Returns a random element from the current set of elements (it's guaranteed that at least one element exists when this method is called). Each element must have the same probability of being returned.
You must implement the functions of the class such that each function works in average O(1) time complexity.
*/

// Solution: O(1) for all operations, O(n) space
/*
This question is NOT asking us to implement a hash table. We don't have to because hashtables don't support O(1) get random. The main crux of the problem is supporting the O(1) get random, so we are allowed to use hash tables.

We keep a mapping of inserted data to the indexes they will occur in in a list. If we just wanted O(1) insert and remove, we could use an object (basically creating a wrapper class), and map values to themselves. For instance insert 5 would be: this.mapping[5] = 5; But here, we use the key to represent the number, and the value to represent an index at which we store the value in an array. To get a random element, we select a random element from the array. It's as if we converted our mapping into an array and chose a random element from that, but we do it only once, instead of every time we want to get a random element (which would be O(n)). When we add an element, push it to the array and add it to the mapping. When we remove an element, say: [1, 4, 2] and we want to remove 1, we need to preserve the indices of our elements in the array. We can't start to use tombstones because then getrandom will fail. We also cannot use an offset mechanic where we splice out the element because 1) splicing from the middle will be O(n) regardless of if we use a deque, and splicing from the middle would change the offset for only some elements. Instead, we overwrite the element we want to remove with our last element, then pop the last element off. We also update that element to have a new index.
*/

var RandomizedSet = function () {
  this.mapping = {}; // maps inserted data to the index they occur in random, so that when we remove an element, we can remove it in O(1) from the random
  this.random = [];
};

RandomizedSet.prototype.insert = function (val) {
  if (val in this.mapping) {
    return false;
  }
  // insert to the end
  const insertLocation = this.random.length;
  this.random.push(val);
  // store index
  this.mapping[val] = insertLocation;
  return true;
};

RandomizedSet.prototype.remove = function (val) {
  if (val in this.mapping) {
    // find where to remove it
    const removalLocation = this.mapping[val];
    this.random[removalLocation] = this.random[this.random.length - 1];
    this.random.pop();
    this.mapping[this.random[removalLocation]] = removalLocation;
    delete this.mapping[val];
    return true;
  }
  return false;
};

RandomizedSet.prototype.getRandom = function () {
  const randomIndex = Math.floor(Math.random() * this.random.length);
  return this.random[randomIndex];
};

// takeaways from a linear probing attempt
/*
0) Misunderstood the question. This question is NOT asking us to implement a hash table in any way. We don't have to because hashtables don't support O(1) get random. The main crux of the problem is supporting the O(1) get random, so we are allowed to use hash tables.

1) tombstones are useful, for instance say we insert a 7: [7] and then a -7, which gets linearly probed by 1 index: [7, -7], then we remove the 7: [undefined, -7], when we search for -7 we will see that we don't have it, so we would need to use a tombstone.

2) get random doesn't work well without explicitly tracking the inserted data in a compressed array, because we have lots of empty values it's hard to find a random value (since we have to keep generating random indices and checking them). We also can't generate a random index then iterate, consider: [1, undefined, undefined, 2], 3/4 of the indices generated will lead to 2

3) When we resize, we need to rehash all the elements, otherwise when we remove or insert an element, our index will be computed off of the new array length, yielding corrupt results. We can also remove the tombstones when we resize, since we will be rehashing everything anyways.

4) When we probe, we can do so quadratically or exponentially to reduce clustering, since we would have many smaller clusters, as opposed to one large cluster, which would in turn grow even larger as elements are sucked into that clustery

5) Instead of making the array start with some amount of filled elements, we can just maintain a size variable and resize when we hit a certain threshold (by just changing the size variable), since the arrays are dynamic anyway and will resize automatically


Overall, the below implementation doesn't really work, due to the get random (everything else works). I also made the array 220k by default as I was debugging and didn't want to deal with array resizing, but it is completely doable as shown by question 706: Design HashMap.
*/

https: var RandomizedSet = function () {
  this.maxIndex = 220000;
  this.storage = new Array(220000).fill(undefined);
  this.numsInserted = 0;
};

RandomizedSet.prototype.insert = function (val) {
  let insertLocation = Math.abs(val % this.storage.length);
  //console.log(`about to insert: ${val} at storage location: ${insertLocation}`);
  while (this.storage[insertLocation] !== undefined) {
    if (this.storage[insertLocation] === val) {
      //console.log(`insertion failed`);
      return false;
    }
    insertLocation++;
    if (insertLocation >= this.storage.length) {
      insertLocation = 0;
    }
  }
  // console.log(`inserted at location: ${insertLocation}`)
  this.storage[insertLocation] = val;
  this.numsInserted++;
  //console.log(`successfully inserted, new storage: ${JSON.stringify(this.storage)}`);
  return true;
};

RandomizedSet.prototype.remove = function (val) {
  let removalLocation = Math.abs(val % this.storage.length);
  //console.log(`about to remove ${val} at index ${removalLocation}`);

  while (this.storage[removalLocation] !== undefined) {
    if (this.storage[removalLocation] === val) {
      this.storage[removalLocation] = "t";
      //console.log(`deletion successful: ${JSON.stringify(this.storage)}`);
      this.numsInserted--;
      return true;
    }
    removalLocation = (removalLocation + 1) % this.storage.length;
  }
  //console.log(`deletion failed`);
  return false;
};

RandomizedSet.prototype.getRandom = function () {
  //console.log(`about to get a random number from: ${JSON.stringify(this.storage)}`);
  if (this.numsInserted === 0) {
    return null;
  }
  let rand;
  do {
    rand = Math.floor(Math.random() * this.storage.length);
  } while (this.storage[rand] === undefined || this.storage[rand] === "t");
  //console.log(`random number found: ${this.storage[rand]}`);
  return this.storage[rand];
};
