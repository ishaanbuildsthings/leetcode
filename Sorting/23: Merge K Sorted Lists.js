// https://leetcode.com/problems/merge-k-sorted-lists/description/
// Difficulty: Hard
// tags: merge sort, linked list

// Solution 1, merge sort, O(n log k) time and O(n) space. N is the total number of nodes, k is the number of linked lists.

/*
To merge multiple linked lists, we can divide the problem. Consider:

lists = [[1,4,5],[1,3,4],[2,6]]

We can divide this into a sub problem, merge:
[[1, 4, 5]] and [[1, 3, 4], [2, 6]]

The first subproblem is already finished, as it has length one. The second sub problem can be merged with a helper function, making [[1, 3, 4, 2, 6]].

Now we merge those two lists, getting [[1, 1, 3, 4, 4, 5, 2, 6]].

If there are k lists, we need to split log k times. Each layer we do a split, we end up doing n total merges as we look at each element. We use auxillary space / memory allocation during the merging. Less space could be used, or even maybe in-place, but this is the simplest starting solution.
*/

// * Solution 2 of mergesort could also be done iteratively. The easiest solution is to iterate through our list of linkedlists, merge each pair into a new list, and then assign that new list to be the list we iterate on again.

var mergeKLists = function (lists) {
  if (lists.length === 0) return null;

  // base cases, we only have one list remaining
  if (lists.length === 1) {
    return lists[0];
  }

  const m = Math.floor(lists.length / 2);
  const leftLists = lists.slice(0, m);
  const rightLists = lists.slice(m);
  const leftSorted = mergeKLists(leftLists);
  const rightSorted = mergeKLists(rightLists);

  const mergedLists = merge2LinkedLists(leftSorted, rightSorted);

  return mergedLists;
};

function merge2LinkedLists(list1, list2) {
  const dummy = new ListNode();
  let current = dummy;

  while (list1 || list2) {
    // if we have both lists, compare them
    if (list1 && list2) {
      if (list1.val <= list2.val) {
        current.next = list1;
        list1 = list1.next;
      } else {
        current.next = list2;
        list2 = list2.next;
      }
      current = current.next;
    }
    // we only have one list
    else {
      while (list1) {
        current.next = list1;
        list1 = list1.next;
        current = current.next;
      }
      while (list2) {
        current.next = list2;
        list2 = list2.next;
        current = current.next;
      }
    }
  }

  return dummy.next;
}
