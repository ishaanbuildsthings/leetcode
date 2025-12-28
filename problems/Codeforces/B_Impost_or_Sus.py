T = int(input())
for _ in range(T):
    r = input()

    # cannot have two u's next to each other in the final output

    # only 'sus' substrings are allowed

    # uuuu
    # u cannot be on the end

    # su

    res = 0

    arr = list(r)
    if arr[0] == 'u':
        res += 1
        arr[0] = 's'
    
    for i in range(1, len(r)):
        # 
        if arr[i] == 's':
            continue # never change an s
        # if our letter is a u, and the previous was a u, we need to change
        if arr[i] == 'u' == arr[i-1]:
            arr[i] = 's'
            res += 1
    if arr[-1] == 'u':
        res += 1
        arr[-1] = 's'


    print(res)

