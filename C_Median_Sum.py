N = int(input())
arr = list(map(int, input().split()))
doable = 1 # technically 0 is not an attainable non-empty subsequence but it makes the code reduce a doable |= (1 << v) operation
for v in arr:
    doable |= doable << v
doable ^= 1 # we need to re-remove the empty subsequence
    
maxDoable = sum(arr)
doables = []
for offset in range(maxDoable + 1):
    if doable & (1 << offset):
        doables.append(offset)
# print(f'{doables=}')
doables.pop()
mid = len(doables) // 2
print(doables[mid] if len(doables) else sum(arr))