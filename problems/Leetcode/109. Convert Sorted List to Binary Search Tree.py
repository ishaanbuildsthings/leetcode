# Definition for singly-linked list.
# class ListNode:
#     def __init__(self, val=0, next=None):
#         self.val = val
#         self.next = next
# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
class Solution:
    def sortedListToBST(self, head: Optional[ListNode]) -> Optional[TreeNode]:
        # could maybe do it without a list at first and just counting to the mid point each time?, but that may be worse TC

        arr = []
        c = head
        while c:
            arr.append(c)
            c = c.next
        
        def build(l, r):
            if l == r:
                return TreeNode(arr[l].val)
            if l > r:
                return None
            mid = (r + l) // 2
            root = TreeNode(arr[mid].val)
            left = build(l, mid - 1)
            right = build(mid + 1, r)
            root.left = left
            root.right = right
            return root
        
        return build(0, len(arr) - 1)
