a, b = map(int, input().split())
 
from functools import lru_cache
 
@lru_cache(maxsize=None)
def dp(isTight, isLeadingZero, last, i, strNum):
  if i == len(strNum):
    return 1
 
  resHere = 0
 
  upperBound = 9 if not isTight else int(strNum[i])
  for nextDigit in range(upperBound + 1):
    newIsTight = isTight and nextDigit == upperBound
    if not isLeadingZero and abs(nextDigit - last) == 0:
      continue
    newLeadingZero = isLeadingZero and nextDigit == 0
    newLast = nextDigit
    resHere += dp(newIsTight, newLeadingZero, newLast, i + 1, strNum)
  return resHere
 
high = dp(True, True, 100, 0, str(b))
low = dp(True, True, 100, 0, str(a-1)) if a else 0
print(high-low)