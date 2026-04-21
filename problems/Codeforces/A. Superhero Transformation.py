import sys
input = sys.stdin.readline
 
s = input().strip()
t = input().strip()
 
import sys
from collections import defaultdict
 
input = sys.stdin.readline
 
 
# s = 'aba'
# t = 'ode'
 
 
if len(s) != len(t):
    # print(f'length fails, ret no')
    print("No")
    exit()
 
for a, b in zip(s, t):
    if a in 'aeiou' and b not in 'aeiou':
        # print(f'mismatch, ret no')
        print("No")
        exit()
    if a not in 'aeiou' and b in 'aeiou':
        # print(f'mis/match, ret no')
        print("No")
        exit()
 
print('Yes')
# groups = defaultdict(list)
# for i, ch in enumerate(t):
#     # print(f'enumerating')
#     groups[ch].append(i)
# # print(f'{groups=}')
 
 
# seenEver = set()
# for indices in groups.values():
#     newSeen = set()
#     for i in indices:
#         newSeen.add(s[i])
#     if any(ch in seenEver for ch in newSeen):
#         print("No")
#         exit()
#     seenEver.update(newSeen)
 
 
 
# print("Yes")