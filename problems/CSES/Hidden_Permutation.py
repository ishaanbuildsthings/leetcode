n = int(input())

def ask(i, j):
    print('?', i, j, flush=True)
    result = input()
    return result == 'YES'

def mergeSort(indices):
    if len(indices) <= 1:
        return indices
    L = len(indices)
    left = indices[:L//2]
    right = indices[L//2:]
    leftSorted = mergeSort(left)
    rightSorted = mergeSort(right)
    s = []
    i = j = 0
    while i < len(leftSorted) and j < len(rightSorted):
        if ask(leftSorted[i], rightSorted[j]):
            s.append(leftSorted[i])
            i += 1
        else:
            s.append(rightSorted[j])
            j += 1
    while i < len(leftSorted):
        s.append(leftSorted[i])
        i += 1
    while j < len(rightSorted):
        s.append(rightSorted[j])
        j += 1
    return s

merged = mergeSort(list(range(1, n + 1)))

answer = [0] * (n + 1)
for rank in range(n):
    answer[merged[rank]] = rank + 1

print('!', *answer[1:], flush=True)