class Solution:
    def distributeCandies(self, candies: int, num_people: int) -> List[int]:
        # find the largest X where we can give all 1...X

        # X*(X+1)/2 <= candies
        # 
        # x^2 + X <= 2 * candies
        # x^2 + x - 2*candies <= 0
        # ax^2 + bx + c = 0, use quadratic formula
        # x = (-b +/ sqrt(b^2 - 4ac)) / 2a
        # x = (-1 +/ sqrt(1 + 8candies)) / 2
        # x = floor of that since we go down

        x = ((-1 + sqrt(1 + 8 * candies)) / 2) // 1
        totalWithX = (x * (x + 1)) // 2
        remainder = candies - totalWithX
        participant = int(x) % num_people

        fullCycles = x // num_people
        remain = x % num_people
        res = [0] * num_people
        for i in range(num_people):
            gainsHere = fullCycles + (1 if (i + 1) <= remain else 0)

            # (i+1) + (n+i+1) + (2n+i+1) + ...
            fromi1 = (i + 1) * gainsHere

            nsgained = (gainsHere - 1) * (gainsHere) // 2
            fromns = nsgained * num_people

            total = fromi1 + fromns

            res[i] = int(total)
        
        res[participant] += int(remainder)
        
        return res
