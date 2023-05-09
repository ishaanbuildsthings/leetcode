// https://leetcode.com/problems/middle-of-the-linked-list/description/
// Difficulty: Easy
// tags: linked list, slow and fast pointers

// Create two pointers, increment the fast one twice as fast. Once the fast one is at the end, return the slow one.

var middleNode = function (head) {
  let slowPointer = head;
  let fastPointer = head;
  // don't run if fastPointer was set to null, or if fastPointer is the last element
  while (fastPointer && fastPointer.next) {
    fastPointer = fastPointer.next.next;
    slowPointer = slowPointer.next;
  }
  return slowPointer;
};
