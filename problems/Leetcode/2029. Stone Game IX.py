class Solution:
    def stoneGameIX(self, stones: List[int]) -> bool:
        
        ones = sum(1 if x % 3 == 1 else 0 for x in stones)
        twos = sum(1 if x % 3 == 2 else 0 for x in stones)
        threes = sum(1 if x % 3 == 0 else 0 for x in stones)

        # try alice picks a 1 first
        if ones:
            ones -= 1
            if threes % 2 == 0:
                turn = 'bob'
            else:
                turn = 'alice'

            if ones < twos:
                if turn == 'bob':
                    return True
            elif ones > twos + 1:
                if turn == 'alice':
                    return True

            ones += 1

        # try alice picks a 2 first
        if twos:
            twos -= 1
            if threes % 2 == 0:
                turn = 'bob'
            else:
                turn = 'alice'

            if twos < ones:
                if turn == 'bob':
                    return True
            elif twos > ones + 1:
                if turn == 'alice':
                    return True

            twos += 1

        return False