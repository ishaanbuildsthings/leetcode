import math
n, k = map(int, input().split())
A = list(map(int, input().split()))
res = 0
fmask = (1 << k) - 1

maskLcm = [0] * (fmask + 1)
for b in range(k):
    num = A[b]
    maskLcm[1 << b] = num
for mask in range(1, fmask + 1):
    if bin(mask).count('1') == 1:
        continue
    msb = mask.bit_length() - 1 # shiftAmount
    maskWithoutMsb = mask ^ (1 << msb)
    val = A[msb]
    oldLcm = maskLcm[maskWithoutMsb]
    # -1 denotes sentinel that the lcm is too big
    if oldLcm == -1:
        newLcm = -1
    else:
        newLcm = math.lcm(maskLcm[maskWithoutMsb], val)
        if newLcm > n:
            newLcm = -1
    maskLcm[mask] = newLcm

for mask in range(1, fmask + 1):
    # lcm = 1
    # flag = False
    # for b in range(k):
    #     if (1 << b) & mask:
    #         lcm = math.lcm(lcm, A[b])
    #         if lcm > n:
    #             flag = True
    #             break
    # if flag:
    #     continue
    # divisible = n // lcm
    maskLcmVal = maskLcm[mask]
    # if this LCM was too big
    if maskLcmVal == -1:
        continue
    divisible = n // maskLcmVal
    isAdding = mask.bit_count() % 2 == 1
    if isAdding:
        res += divisible
    else:
        res -= divisible
print(res)
