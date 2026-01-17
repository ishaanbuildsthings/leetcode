def solve(l1,b1,l2,b2,l3,b3):
    if l1 == l2 == l3:
        # if all widths the same, we vertically stack
        return l1 == b1 + b2 + b3
    
    # if largest width is second largest width but third is different, no way
    if l1 == l2:
        return False
    
    # all widths different

    # stack the top 2 side by side
    if l1 != (l2 + l3):
        return False
    
    # if their heights arent the same we fail
    if b2 != b3:
        return False
    
    if b2 + b1 == l1:
        return True
    
    return False


    # l3xb3 is smallest
    # l2xb2 bigger
    # l1xb1 contains all

t = int(input())
for _ in range(t):
    l1, b1, l2, b2, l3, b3 = map(int,input().split())
    ans = solve(l1,b1,l2,b2,l3,b3)
    if ans:
        print("YES")
    else:
        ans = solve(b1,l1,b2,l2,b3,l3)
        if ans:
            print("YES")
        else:
            print("NO")

        # x x
        # x x
        # x x

        # x
        # x

        # x