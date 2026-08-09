# count of elements < X 
def countLtX(sl, x):
    return sl.bisect_left(x)
 
# count of elements <= X 
def countLteX(sl, x):
    return sl.bisect_right(x)
 
# count of elements > X
def countGtX(sl, x):
    return len(sl) - sl.bisect_right(x)
 
# count of elements >= X
def countGteX(sl, x):
    return len(sl) - sl.bisect_left(x)
 
# count of elements in value range L...R
def countInRange(sl, l, r):
    if l > r:
        return 0
    return sl.bisect_right(r) - sl.bisect_left(l)

def largestLtX(sl, x):
    i = sl.bisect_left(x)
    return sl[i - 1] if i else None

def largestLteX(sl, x):
    i = sl.bisect_right(x)
    return sl[i - 1] if i else None

def largestGteX(sl, x):
    return sl[-1] if sl and sl[-1] >= x else None

def largestGtX(sl, x):
    return sl[-1] if sl and sl[-1] > x else None