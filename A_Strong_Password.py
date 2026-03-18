def solve():
    # print('----')
    s = input()
    if len(s) == 1:
        return (s + 'a') if s != 'a' else s + 'c'
    sameI = None
    for i in range(len(s) - 1):
        if s[i] == s[i + 1]:
            sameI = i
            break
    # any pair the same
    if sameI is not None:
        # print(f'some pair is the same at {sameI=}')
        different = 'g' if s[sameI] == 'a' else 'a'
        return s[:sameI+1] + different + s[sameI+1:]
    # no two are the same
    different = 'a' if (s[0] != 'a' and s[1] != 'a') else 'b' if (s[0] != 'b' and s[1] != 'b') else 'c'
    # print(f'{different=}')
    return s[0] + different + s[1:]


t = int(input())
for _ in range(t):
    ans = solve()
    print(ans)
