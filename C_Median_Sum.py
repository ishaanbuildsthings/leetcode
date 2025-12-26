N = int(input())
arr = list(map(int, input().split()))
doable = 1 # technically 0 is not an attainable non-empty subsequence but it makes the code reduce a doable |= (1 << v) operation
for v in arr:
    doable |= doable << v
doable ^= 1 # we need to re-remove the empty subsequence

tot = sum(arr)
if tot % 2 == 0 and (doable >> (tot//2)) & 1:
    print(tot//2)
else:
    need = tot//2 + 1 # strictly greater than T/2
    shifted = doable >> need
    lsb = shifted & -shifted
    pos = lsb.bit_length() - 1
    print(need + pos)