// https://leetcode.com/problems/flatten-a-multilevel-doubly-linked-list/description/
// Difficulty: Medium
// tags: inorder, linked list

// Problem
/*
Simplified:
We have a doubly linked list. Each node may also have a child that is another doubly linked list. We need to flatten them and set all childs to null.

Detailed:
You are given a doubly linked list, which contains nodes that have a next pointer, a previous pointer, and an additional child pointer. This child pointer may or may not point to a separate doubly linked list, also containing these special nodes. These child lists may have one or more children of their own, and so on, to produce a multilevel data structure as shown in the example below.

Given the head of the first level of the list, flatten the list so that all the nodes appear in a single-level, doubly linked list. Let curr be a node with a child list. The nodes in the child list should appear after curr and before curr.next in the flattened list.

Return the head of the flattened list. The nodes in the list must have all of their child pointers set to null.
*/

// Solution 1, O(n) time and O(n) space. Not the best as our space is all the nodes, not just the height.
/*
Do an inorder traversal, pushing all the elements to a stack. Afterwards, iterate through the stack rewiring the nodes.
*/

var flatten = function (head) {
  const nodes = [];

  function dfs(node) {
    if (!node) {
      return;
    }

    nodes.push(node);
    dfs(node.child);
    dfs(node.next);
  }

  dfs(head);

  for (let i = 0; i < nodes.length; i++) {
    const node = nodes[i];
    if (i === 0) {
      node.prev = null;
    } else {
      node.prev = nodes[i - 1];
    }

    if (i === nodes.length - 1) {
      node.next = null;
    } else {
      node.next = nodes[i + 1];
    }

    node.child = null;
  }

  return nodes[0];
};

// Solution 2, iterative, same complexities as solution 1
/*
Add nodes to a stack. Whenever we have a child, add a memo of the node. Then start adding the children. Once we run out of children, pop from the memo and continue.
*/

var flatten = function (head) {
  if (!head) return null;

  const stack = [head];
  const memos = [];

  while (true) {
    const node = stack[stack.length - 1];
    if (node.child) {
      if (node.next) {
        memos.push(node);
      }
      stack.push(node.child);
    } else if (node.next) {
      stack.push(node.next);
    } else {
      if (memos.length > 0) {
        const memo = memos.pop();
        if (memo.next) {
          stack.push(memo.next);
        }
      } else {
        break;
      }
    }
  }

  for (let i = 0; i < stack.length; i++) {
    const node = stack[i];
    if (i === 0) {
      node.prev = null;
    } else {
      node.prev = stack[i - 1];
    }

    if (i === stack.length - 1) {
      node.next = null;
    } else {
      node.next = stack[i + 1];
    }

    node.child = null;
  }

  return stack[0];
};

// Solution 3, O(n) time and O(n) (height) space. Recursive solution. The dfs function returns the tail of the list. We first wire in the previous node. Memoize the next node. DFS down to the child. Reset the child to null. Then take that DFS going down and wire it into the next node. The dfs function itself returns the tail at the end. A bit confusing to implement.

var flatten = function (head) {
  // dfs iterates through a nodes child, rewiring, then returns the tail, so that we can wire the tail into .next
  function dfs(prev, node) {
    // if we reach null, return the tail of what we reached, in the base case this is just the original parent node
    if (!node) {
      return prev;
    }

    //preorder, process node first
    node.prev = prev;
    prev.next = node;

    const tempNext = node.next;
    const tail = dfs(node, node.child);

    node.child = null;

    return dfs(tail, tempNext);
  }

  const dummy = new Node();
  dfs(dummy, head);
  if (!dummy.next) return null;

  dummy.next.prev = null;
  return dummy.next;
};
