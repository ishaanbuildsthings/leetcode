// https://leetcode.com/problems/reverse-linked-list/description/
// Difficulty: Easy
// tags: linked list
/*
Given the head of a singly linked list, reverse the list, and return the reversed list.
*/

// Solution
// O(n) time to iterate through the list and O(1) storage. Maintain a pointer to the previous node, memo the next node, rewire the connection, and iterate.

const reverseList = function (head) {
  let prev = null; // track the previous node
  while (head) {
    const next = head.next;
    head.next = prev;
    prev = head; // maintain a pointer for previous
    head = next; // iterate
  }
  return prev;
};
