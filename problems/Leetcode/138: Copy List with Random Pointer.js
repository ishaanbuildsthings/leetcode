// https://leetcode.com/problems/copy-list-with-random-pointer/description/
// Difficulty: Medium

// Problem
/*
Simplified: We are given a linked list, where each element also has a .random pointer that points to a random other element in the linked list (or null), construct a deep copy of the linked list.
*/

// Solution 1, O(n) time and O(n) space
/*
Create a dummy node which will help track the head of the output list. Iterate over the original list, creating clones with .next pointers being appended to dummy. We also populate a Map which maps old nodes to new nodes. Then, iterate over the old list again, look up the random node in the map, and receive the corresponding random node in the new list, wire that into the new list.

The more complicated original solution I wrote used two maps, one that mapped old nodes to the indices they occured, and one that mapped indices to new nodes. Then we can look up the old node, find the index, look up the index, and find the corresponding new node. But this solution just reduces to the one map solution.
*/
// * There is also an O(1) space solution, where we interleave the original list and the new list. For instance 1o->1n->2o->2n (o=old, n=new). To assign the .random on 1n, we look at the the .random of 1o, and take whatever that is pointing to, which will be the 1n.random, then we separate the lists

var copyRandomList = function (head) {
  const dummy = new Node();

  // iterate over the input, creating the .next chain for the output, and a mapping of old nodes to new nodes
  let old = head;
  let current = dummy;

  const mapping = new Map(); // maps original nodes : new nodes
  while (old) {
    const newNode = new Node(old.val);

    mapping.set(old, newNode);

    current.next = newNode;
    current = current.next;
    old = old.next;
  }
  // now dummy.next points to a duplicated list with correct .nexts

  old = head;
  current = dummy.next;
  while (old) {
    const newListRandom = mapping.get(old.random);
    current.random = newListRandom;
    old = old.next;
    current = current.next;
  }

  return dummy.next;
};
