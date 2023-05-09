// https://leetcode.com/problems/merge-two-sorted-lists/description/
// Difficulty: Easy
// tags: linked list

// Problem
/*
Merge two sorted linked lists and return it as a sorted list. The list should be made by splicing together the nodes of the first two lists.
*/

// Solution
// O(Math.min(n, m)) time and O(1) space. Use a dummy node to track the head of the list, and a tail pointer to track where we append the next node. Iterate through the two lists, compare the values, append the smaller one to the tail, and increment that pointer. If one list is longer than the other, append the rest of that list to the tail.

const mergeTwoLists = function (l1, l2) {
  const dummy = new ListNode();
  let tail = dummy; // to track where we append

  // as long as we have two lists, compare them, append the smaller one to our tail, and increment that pointer
  while (l1 && l2) {
    if (l1.val <= l2.val) {
      tail.next = l1;
      l1 = l1.next;
    } else {
      tail.next = l2;
      l2 = l2.next;
    }
    tail = tail.next;
  }
  if (l1) {
    tail.next = l1;
  } else {
    tail.next = l2;
  }
  return dummy.next;
};

// You can also not use a dummy node, like this:

var mergeTwoLists2 = function (l1, l2) {
  if (!l1) return l2;
  if (!l2) return l1;

  let head;
  if (l1.val <= l2.val) {
    head = l1;
    l1 = l1.next;
  } else {
    head = l2;
    l2 = l2.next;
  }
  let tail = head;

  while (l1 && l2) {
    if (l1.val <= l2.val) {
      tail.next = l1;
      l1 = l1.next;
    } else {
      tail.next = l2;
      l2 = l2.next;
    }
    tail = tail.next;
  }

  if (l1) {
    tail.next = l1;
  } else {
    tail.next = l2;
  }

  return head;
};
