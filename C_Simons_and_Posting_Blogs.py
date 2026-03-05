from functools import cmp_to_key
from collections import deque

t = int(input())

# smallest backwards blog goes last
for _ in range(t):
    # print('-------------')
    n = int(input())
    blogs = []
    for _ in range(n):
        blog = list(map(int, input().split()))[1:]
        blog2 = []
        for i in range(len(blog) - 1, -1, -1):
            if blog[i] in blog2:
                continue
            blog2.append(blog[i])
        blogs.append(blog2)
    # print(blogs)
    res = []
    for _ in range(n):
        if not blogs:
            break
        smallest = min(blogs)
        # print(f'{smallest=}')
        res.extend(smallest)
        blogSet = set(smallest)
        for i in range(len(blogs)):
            blogs[i] = [x for x in blogs[i] if x not in blogSet]
        blogs = [blog for blog in blogs if blog]
        # print(f'blogs now: {blogs}')
    print(*res)
    # def compare(a, b):
    #     a = a[::-1]
    #     b = b[::-1]
    #     # a = sorted(a, reverse=True)
    #     # b = sorted(b, reverse=True)
    #     # print(f'{a=} {b=}')
    #     for i in range(min(len(a), len(b))):
    #         if a[i] < b[i]:
    #             return 1
    #         elif a[i] > b[i]:
    #             return -1
    #     if len(a) < len(b):
    #         return 1
    #     return -1

    # # print(compare([1, 2, 4, 3, 1], [4, 1]))
    # blogs.sort(key=cmp_to_key(compare))
    # print(f'sorted blogs: {blogs}')
    # res = deque()
    # for blog in blogs:
    #     for v in blog:
    #         if v not in res:
    #             res.appendleft(v)
    #         else:
    #             for i in range(len(res)):
    #                 if res[i] == v:
    #                     del res[i]
    #                     break
    #             res.appendleft(v)
    # print(*res)

    