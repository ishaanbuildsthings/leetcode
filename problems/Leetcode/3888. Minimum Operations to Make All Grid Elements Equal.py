class Solution:
    def minOperations(self, grid: list[list[int]], k: int) -> int:
        # edge case, if k=1 my code won't work as we cannot solve for T at any cell since they are all tautologies
        if k == 1:
            mx = max(max(rw) for rw in grid)
            res = sum(mx - grid[r][c] for r in range(len(grid)) for c in range(len(grid[0])))
            return res
            
        # call the smallest possible number, that we can set everything to, T
        # we don't know what T is yet
        # but for instance say our grid[0][0] = 3
        # we obviously must add T-3 to this cell
        # (we are processing cells left to right, top to bottom), so this is kinda assuming no prior cells have boosted (0,0)
        # which is obviously the case since 0,0 is the top left

        height = len(grid)
        width = len(grid[0])

        # we will add things like coeff*T + constant to each cell

        coeff = [[0] * (width+1) for _ in range(height+1)]
        constant = [[0] * (width+1) for _ in range(height+1)]
        T = None
        loT = 0
        hiT = inf

        for r in range(height - k + 1):
            for c in range(width - k + 1):
                above = coeff[r - 1][c] if r > 0 else 0
                left = coeff[r][c - 1] if c > 0 else 0
                diag = coeff[r - 1][c - 1] if r > 0 and c > 0 else 0
                coeff[r][c] += above + left - diag

                above = constant[r - 1][c] if r > 0 else 0
                left = constant[r][c - 1] if c > 0 else 0
                diag = constant[r - 1][c - 1] if r > 0 and c > 0 else 0
                constant[r][c] += above + left - diag

                a = coeff[r][c]
                b = constant[r][c]

                # we have currently boosted this cell by a*T + b

                # T = aT + b + grid[r][c] + ops
                # we need this cell to reach T
                # so ops = T - grid[r][c] - (a*T + b)
                # = (1-a)*T + (-grid[r][c] - b)
                ca = 1 - a
                cb = -grid[r][c] - b

                # ops = ca*T + cb must be non-negative
                # ca*T + cb >= 0
                # if ca > 0: T >= -cb/ca (lower bound)
                # if ca < 0: T <= -cb/ca (upper bound, inequality flips)
                # if ca == 0: cb must be >= 0 on its own
                if ca > 0:
                    bound = (-cb + ca - 1) // ca  # ceiling division
                    if bound > loT:
                        loT = bound
                elif ca < 0:
                    bound = -cb // ca  # floor division
                    if bound < hiT:
                        hiT = bound
                else:
                    if cb < 0:
                        return -1

                r2 = r + k
                c2 = c + k
                # apply range add
                coeff[r][c] += ca; coeff[r][c2] -= ca
                coeff[r2][c] -= ca; coeff[r2][c2] += ca
                constant[r][c] += cb; constant[r][c2] -= cb
                constant[r2][c] -= cb; constant[r2][c2] += cb

        # if lower bound exceeds upper bound, no valid T exists
        if loT > hiT:
            return -1

        # now we have done all the range adds, finish the 2d sweep so every cell is up to date
        for r in range(height):
            for c in range(width):
                if (r <= height - k) and (c <= width - k):
                    continue
                above = coeff[r - 1][c] if r > 0 else 0
                left = coeff[r][c - 1] if c > 0 else 0
                diag = coeff[r - 1][c - 1] if r > 0 and c > 0 else 0
                coeff[r][c] += above + left - diag

                above = constant[r - 1][c] if r > 0 else 0
                left = constant[r][c - 1] if c > 0 else 0
                diag = constant[r - 1][c - 1] if r > 0 and c > 0 else 0
                constant[r][c] += above + left - diag

        # all the first cells are exactly = to K by definition because we forced them to be, so we need to use a different cell
        # otherwise the value we solve for T is tautologically true
        # for instance say grid[0][0] is 10 and so we add T - 10 to the cell
        # now the cell is T, but for any T... we cannot determine T from this

        # however note that for a cell, if we divide by 1 - coeff[r][c] and coeff[r][c] is 1, it is impossible
        # this doesn't mean T is incomputable, it just means this cell gives us no info
        # so we loop through any cell that can give us info until we find one that does
        # remember the original equation was (1 - a) * T = grid[r][c] + b
        # we only divided by (1-a) to isolate T, but that doesn't mean suddenly T is impossible to attain if a=1
        T = None
        for r in range(height):
            for c in range(width):
                if r + k <= height and c + k <= width:
                    continue
                a = coeff[r][c]
                b = constant[r][c]
                lhs = 1 - a
                rhs = grid[r][c] + b
                if lhs == 0:
                    if rhs != 0:
                        # invalid cell, we failed then
                        return -1
                    # if both are 0, no info, move on
                    continue
                # float T, invalid
                if rhs % lhs != 0:
                    return -1
                T = rhs // lhs
                break
            if T is not None:
                break
    
        # if T is still none it basically means every single non-valid cell had the equation 0 = 0. T cancelled out of every constraint, every non-valid cell is satisfied for any value of T

        # this happens when the grid is exactly k×k, there's one valid corner at (0,0), and the operation there adds T - grid[0][0] to every cell. cell (0,1) gets boost T - grid[0][0], so its equation becomes:
        # T = grid[0][1] + (T - grid[0][0])
        
        if T is None:
            T = loT
        elif T < loT or T > hiT:
            # non-valid cells pinned T to a value outside the feasible range
            return -1

        # verify all the formulas match to the desired T
        for r in range(height):
            for c in range(width):
                total = grid[r][c] + coeff[r][c] * T + constant[r][c]
                if total != T:
                    return -1
        
        # now compute the actual amount of operations used in real numbers
        # we could use the # of times we did a range add with top left cell (r, c) for each r, c but I didn't save that from the first pass
        # instead, I can compute how much each cell gets boosted by, then divide that total boosts by k^2
        res = 0
        for r in range(height):
            for c in range(width):
                added = (coeff[r][c] * T) + constant[r][c]
                res += added
        
        return res // (k**2)