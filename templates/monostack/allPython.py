# nearest index to the left that is strictly smaller than arr[i]
# -1 if none, pop while arr[st[-1]] >= arr[i]
def rightmostOnLeftLtNum(arr):
    n = len(arr)
    st = []
    res = [-1] * n
    for i in range(n):
        while st and arr[st[-1]] >= arr[i]:
            st.pop()
        res[i] = st[-1] if st else -1
        st.append(i)
    return res

# nearest index to the left that is smaller than or equal to arr[i]
# -1 if none, pop while arr[st[-1]] > arr[i]
def rightmostOnLeftLteNum(arr):
    n = len(arr)
    st = []
    res = [-1] * n
    for i in range(n):
        while st and arr[st[-1]] > arr[i]:
            st.pop()
        res[i] = st[-1] if st else -1
        st.append(i)
    return res

# nearest index to the left that is strictly greater than arr[i]
# -1 if none, pop while arr[st[-1]] <= arr[i]
def rightmostOnLeftGtNum(arr):
    n = len(arr)
    st = []
    res = [-1] * n
    for i in range(n):
        while st and arr[st[-1]] <= arr[i]:
            st.pop()
        res[i] = st[-1] if st else -1
        st.append(i)
    return res

# nearest index to the left that is greater than or equal to arr[i]
# -1 if none, pop while arr[st[-1]] < arr[i]
def rightmostOnLeftGteNum(arr):
    n = len(arr)
    st = []
    res = [-1] * n
    for i in range(n):
        while st and arr[st[-1]] < arr[i]:
            st.pop()
        res[i] = st[-1] if st else -1
        st.append(i)
    return res

# nearest index to the right that is strictly smaller than arr[i]
# n if none, pop while arr[st[-1]] >= arr[i]
def leftmostOnRightLtNum(arr):
    n = len(arr)
    st = []
    res = [n] * n
    for i in range(n - 1, -1, -1):
        while st and arr[st[-1]] >= arr[i]:
            st.pop()
        res[i] = st[-1] if st else n
        st.append(i)
    return res

# nearest index to the right that is smaller than or equal to arr[i]
# n if none, pop while arr[st[-1]] > arr[i]
def leftmostOnRightLteNum(arr):
    n = len(arr)
    st = []
    res = [n] * n
    for i in range(n - 1, -1, -1):
        while st and arr[st[-1]] > arr[i]:
            st.pop()
        res[i] = st[-1] if st else n
        st.append(i)
    return res

# nearest index to the right that is strictly greater than arr[i]
# n if none, pop while arr[st[-1]] <= arr[i]
def leftmostOnRightGtNum(arr):
    n = len(arr)
    st = []
    res = [n] * n
    for i in range(n - 1, -1, -1):
        while st and arr[st[-1]] <= arr[i]:
            st.pop()
        res[i] = st[-1] if st else n
        st.append(i)
    return res

# nearest index to the right that is greater than or equal to arr[i]
# n if none, pop while arr[st[-1]] < arr[i]
def leftmostOnRightGteNum(arr):
    n = len(arr)
    st = []
    res = [n] * n
    for i in range(n - 1, -1, -1):
        while st and arr[st[-1]] < arr[i]:
            st.pop()
        res[i] = st[-1] if st else n
        st.append(i)
    return res