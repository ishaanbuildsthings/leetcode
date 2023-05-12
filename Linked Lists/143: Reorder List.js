// https://leetcode.com/problems/reorder-list/description/
// Difficulty: Medium

// Problem
/*
Simple explanation:
Given a linked list like 1->2->3->4->5->
reorder it to be 1->5->2->4->3->
Detailed explanation:
ou are given the head of a singly linked-list. The list can be represented as:

L0 → L1 → … → Ln - 1 → Ln
Reorder the list to be on the following form:

L0 → Ln → L1 → Ln - 1 → L2 → Ln - 2 → …
*/

// Solution
// O(n) time and O(1) space. Iterate over the linked list, creating previous pointers to make it a doubly linked list. We do this so we can iterate backwards. Create a head and tail pointer. Create a dummy pointer which we will add nodes to to form the turbulent linked list. Toggle back and forth between adding the head and tail pointer to the list, until head meets tail. Then add the final pointer, and sever the ending connection.

// * Another solution would be to reverse the second half of the list, then merge that with the first half

var reorderList = function (head) {
  let headReverser = head;
  headReverser.prev = null;
  while (headReverser && headReverser.next) {
    headReverser.next.prev = headReverser;
    headReverser = headReverser.next;
  }

  let tail = headReverser;

  // now we have a tail and head pointer, and a doubly linked list
  const dummy = new ListNode();
  let dummyTail = dummy;
  let sideToAdd = 0;
  while (head !== tail) {
    if (sideToAdd === 0) {
      dummyTail.next = head;
      sideToAdd = 1;
      head = head.next;
      dummyTail = dummyTail.next;
    } else if (sideToAdd === 1) {
      dummyTail.next = tail;
      sideToAdd = 0;
      tail = tail.prev;
      dummyTail = dummyTail.next;
    }
  }
  // once head === tail, we have one more element to add, so add that to the tail
  dummyTail.next = head;
  // sever the final connection, consider:
  // 1->2->3->4->
  /*
    after dummy points to 1, head points to 2, tail to 4
    now our dummy chains to 4, head points to 2, tail to 3
    now our dummy chains to 2, head points to 3, tail to 3
    we add the final chain to 3, but we need to sever the connection from 3 to 4 at the end
    */
  dummyTail.next.next = null;
};
