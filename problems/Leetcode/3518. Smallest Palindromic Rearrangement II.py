class Solution:
    def smallestPalindrome(self, s: str, k: int) -> str:
        resHalf = [None] * (len(s) // 2)
        middleLetter = None
        c = Counter(s)
        for letter in c:
            if c[letter] % 2:
                middleLetter = letter
        
        for key in c:
            c[key] = c[key] // 2
        
        
            
        def couldMake(counter, spotsRemaining):
            # print(f'curr counter: {counter}')
            # print(F'initial spots remaining: {spotsRemaining}')
            if not spotsRemaining:
                return 1
            make = 1
            for key in counter:
                if not spotsRemaining:
                    return make
                amount = counter[key]
                # print(f'amount: {amount} of letter: {key}, spots remaining: {spotsRemaining}')
                ways = math.comb(spotsRemaining, amount)
                make *= ways
                spotsRemaining -= amount
                if make > k:
                    return k
                    # return 'OVERFLOW'
            return make
        
        ABC = set()
        for key in c:
            if c[key]:
                ABC.add(key)
        ABC = sorted(ABC)
        
        remain = k
                
            
        
        for i in range(len(resHalf)):
            # if i were to put this letter, how many strings could i make
            madeBefore = 0
            # print(resHalf)
            # print(f'i={i}')
            # print(f'spots remaining: {len(resHalf) - i - 1}')
            for letter in ABC:
                if not c[letter]:
                    continue
                c[letter] -= 1
                makeable = couldMake(c, len(resHalf) - i - 1)
                c[letter] += 1
                if madeBefore + makeable >= k:
                    k -= madeBefore
                    resHalf[i] = letter
                    c[letter] -= 1
                    break
                madeBefore += makeable
            if resHalf[i] is None:
                return ''
                
                
        
        
        
        
        
        
        if None in resHalf:
            return ''
        
        if len(s) % 2:
            firstHalf = ''.join(resHalf)
            return firstHalf + middleLetter + firstHalf[::-1]
        firstHalf = ''.join(resHalf)
        return firstHalf + firstHalf[::-1]
        
            
        