n = int(input())
s = input()

if '0' not in s:
    print(s)
    exit()
if '1' not in s:
    print(0)
    exit()
first1 = s.index('1')
s = s[first1:]
first0 = s.index('0')
answer = s
n = len(s)

def makeOr(substring):
    m = len(substring)
    result = list(s)
    for i in range(len(substring)):
        if result[n - i - 1] == '1':
            continue
        if substring[m - i - 1] == '1':
            result[n - i - 1] = '1'
    for i in range(len(result)):
        if result[i] != '0':
            return ''.join(result[i:])
    return '0'
        
prefixesThatCanReach = first0 + 1
pfSize = n
while prefixesThatCanReach > 0:
    prefixesThatCanReach -= 1
    pf = s[:pfSize]
    resultHere = makeOr(pf)
    if len(resultHere) > len(answer):
        answer = resultHere
    elif len(resultHere) == len(answer):
        answer = max(answer, resultHere)
    pfSize -= 1
for i in range(len(answer)):
    if answer[i] != '0':
        print(answer[i:])
        exit()
print(0)
