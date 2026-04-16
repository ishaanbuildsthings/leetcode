# Definition for singly-linked list.
# class ListNode:
#     def __init__(self, val=0, next=None):
#         self.val = val
#         self.next = next
class Solution:
    def reverseEvenLengthGroups(self, head: Optional[ListNode]) -> Optional[ListNode]:
            
            # reverses a change strictly in between pre and post
            # so pre -> a -> b -> c -> post
            # becomes
            # pre -> c -> b -> a -> post
            # note that pre needs to be a real node (so we use a dummy) but post can be None

            # intermediate step
            # pre -> <- a <- b <- c post
            def rev(pre, post):
                prev = pre
                curr = pre.next
                initNext = pre.next
                while curr is not post:
                    nxt = curr.next
                    curr.next = prev
                    prev = curr
                    curr = nxt
                pre.next = prev
                initNext.next = curr

                # pre-> <-a <- b <- c post     curr is post, prev is c
            
            d = ListNode(0, head)
            size = 1
            pre = d
            while True:
                curr = pre.next
                if not curr:
                    break
                
                initNext = curr

                actualSize = 1
                for _ in range(size - 1):
                    if curr.next:
                        curr = curr.next
                        actualSize += 1
                # now curr is the ending of the chain
                post = curr.next

                if actualSize % 2 == 0:
                    rev(pre, post)
                    pre = initNext
                else:
                    pre = curr
                
                size += 1
            
            return d.next




