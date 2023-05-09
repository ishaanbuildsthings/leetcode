//https://leetcode.com/problems/linked-list-cycle/description/
// Difficulty: Easy
// tags: linked list, slow nd fast pointers

// Problem
/*
Given head, the head of a linked list, determine if the linked list has a cycle in it.

There is a cycle in a linked list if there is some node in the list that can be reached again by continuously following the next pointer. Internally, pos is used to denote the index of the node that tail's next pointer is connected to. Note that pos is not passed as a parameter.

Return true if there is a cycle in the linked list. Otherwise, return false.
*/

// Solution
// O(n) time and O(1) space. Use a slow and fast pointer and see if they eventually meet.

const hasCycle = function (head) {
  let slowPointer = head;
  let fastPointer = head;
  while (slowPointer) {
    slowPointer = slowPointer.next;
    if (fastPointer === null) return false;
    if (fastPointer.next === null) return false;
    fastPointer = fastPointer.next.next;
    if (slowPointer === fastPointer) {
      return true;
    }
  }
  return false;
};
