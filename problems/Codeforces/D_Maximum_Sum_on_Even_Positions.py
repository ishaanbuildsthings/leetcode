# 0 1 2 3 4 5 6
# ^         ^

# As we are in range, any odd index gets added, only if our total length is even (O-E or E-O)
# Always end on an odd index and start on an even index for reversing
# we basically need the maximum diff of odd indices over thei

t = int(input())
for _ in range(t):
    n = int(input())
    A = list(map(int, input().split()))
    closed = 0
    open = float('-inf')
    notOpen = 0
    for i, v in enumerate(A):
        nNotOpen = notOpen + v
        nOpen = max(notOpen + (v if i % 2 ))
    dpClosed = 0 # finished reversing
    dpOddOpen = float('-inf') # started reversing at an odd index
    dpEvenOpen = float('-inf')
    dpNotOpen = 0
    for i, v in enumerate(A):
        # If we aren't open, add if this is even
        ndpNotOpen = dpNotOpen + (v if i % 2 == 0 else 0)

        # We can add this element to our closed
        ndpClosed = dpClosed + (v if i % 2 == 0 else 0)

        # If we are open on an odd, and this is an even index, we can close out here
        if i % 2 == 0:
            ndpClosed = max(ndpClosed, dpOddOpen)
        
        # If we are open on an even, and this is odd, we can close
        if i % 2 == 1:
            ndpClosed = max(ndpClosed, dpEvenOpen + v)
        
        # Opens can keep being open or start being open
        ndpOddOpen = dpOddOpen + (v if i % 2 == 1 else 0)
        ndpEvenOpen = dpEvenOpen + (v if i % 2 == 1 else 0)

        if i % 2 == 1:
            ndpOddOpen = max(ndpOddOpen, dpNotOpen + v)
        if i % 2 == 0:
            ndpEvenOpen = max(ndpEvenOpen, dpNotOpen)
        
        dpClosed = ndpClosed
        dpOddOpen = ndpOddOpen
        dpEvenOpen = ndpEvenOpen
        dpNotOpen = ndpNotOpen
        
    
    print(dpClosed)