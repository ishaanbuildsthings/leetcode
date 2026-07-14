class Solution:
    def createGrid(self, m: int, n: int, k: int) -> list[str]:

        # m = 4
        # n = 2
        # k = 3


        # k = 1 trivial

        # k = 2 means 2x2 in top left then restrict

        # k = 3 is doable? don't think so

        # k = 4 means 2x2 in top left and bottom right?

        height = m
        width = n
        grid = [['.' for _ in range(width)] for _ in range(height)]


        twoByTwo = {(0, 0), (0, 1), (1, 0), (1, 1)}


        if k == 1:
            print(f'k=1')
            # only allow leftmost and bottommost
            for r in range(height):
                for c in range(width):
                    if c == 0 or r == height - 1:
                        continue
                    grid[r][c] = '#'

            

                    
        elif k == 2:
            print(f'k=2')
            if min(height, width) == 1:
                return []

            # 2x2 is empty, then go straight down and straight right

            for r in range(height):
                for c in range(width):
                    if (r, c) in twoByTwo:
                        # print(f'in empty 2x2')
                        continue

                    # allow going straight down
                    if c == 1:
                        continue

                    # allow going straight right at the bottom, except for bottom left corner
                    if r == height - 1 and c >= 1:
                        continue

                    grid[r][c] = '#'
                    
                    

                
        elif k == 3:
            print(f'k=3')
            # requires a 2x3 or a 3x2
            if min(height, width) == 1:
                return []

            if max(height, width) <= 2:
                return []

            # at least 1 dimension is 3, both are at least 2

            # if horiz:
            # x x x
            # x x x
            horiz = width >= 3

            twoThree = {(0,0),(0,1),(0,2),(1,0),(1,1),(1,2)}
            

            if horiz:
                print(f'wide 2x3')
                for r in range(height):
                    for c in range(width):
                        if (r, c) in twoThree:
                            continue

                        # go straight down
                        if c == 2:
                            continue

                        # go straight right at the bottom, except for two bottom left
                        if r == height - 1 and c >= 2:
                            continue

                        grid[r][c] = '#'

            
            # x x
            # x x
            # x x
            else:
                print(f'tall 3x2')
                threeTwo = {(0,0),(0,1),(1,0),(1,1),(2,0),(2,1)}
                for r in range(height):
                    for c in range(width):
                        if (r, c) in threeTwo:
                            continue
                        # go straight down
                        if c == 1:
                            continue

                        if r == height - 1 and c >= 1:
                            continue

                        grid[r][c] = '#'
                
            
        elif k == 4:
            print(f'k=4')
            # requires 2x4 or 4x2 or 3x3

            if min(height, width) == 1:
                return []

            # 2x4 or 4x2 case
            if max(height, width) >= 4:

                # x x x x
                # x x x x

                horiz = width >= 4
                twoFour = {(0,0),(0,1),(0,2),(0,3),(1,0),(1,1),(1,2),(1,3)}
    
                if horiz:
                    print(f'wide 2x4')
                    for r in range(height):
                        for c in range(width):
                            if (r, c) in twoFour:
                                continue
    
                            # go straight down
                            if c == 3:
                                continue
    
                            # go straight right at the bottom, except for three bottom left
                            if r == height - 1 and c >= 3:
                                continue
    
                            grid[r][c] = '#'
    
                
                # x x
                # x x
                # x x
                # x x
                else:
                    print(f'tall 4x2')
                    fourTwo = {(0,0),(0,1),(1,0),(1,1),(2,0),(2,1),(3,0),(3,1)}
                    for r in range(height):
                        for c in range(width):
                            if (r, c) in fourTwo:
                                continue
                            # go straight down
                            if c == 1:
                                continue
    
                            if r == height - 1 and c >= 1:
                                continue
    
                            grid[r][c] = '#'


            # 3x3 case
            else:
                if min(height, width) < 3:
                    return []
                if max(height, width) < 3:
                    return []

                # 3x3
                print(f'3x3')

                for r in range(height):
                    for c in range(width):
                        grid[r][c] = '#'

                grid[0][0] = '.'
                grid[0][1] = '.'
                grid[1][0] = '.'
                grid[1][1] = '.'
                grid[1][2] = '.'
                grid[2][1] = '.'
                grid[2][2] = '.'

                for r in range(3, height):
                    grid[r][2] = '.'
                for c in range(2, width):
                    grid[-1][c] = '.'
                

        # print(f'curr grid: {grid}')
        res = []
        for row in grid:
            res.append(''.join(row))

        return res

            