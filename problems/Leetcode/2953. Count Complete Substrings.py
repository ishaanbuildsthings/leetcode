class Solution:
    def countCompleteSubstrings(self, word: str, k: int) -> int:
        windowSizes = []
        for num in range(1, 27):
            if num * k > len(word):
                break
            windowSizes.append(num * k)
        
        res = 0
        
        # check two adj letters
        def checkTwo(char1, char2):
            first = ord(char1) - ord('a')
            second = ord(char2) - ord('a')
            return abs(first - second) <= 2
        
        
        
        def addToResWithSize(size):
            resForThis = 0
            
            counts = defaultdict(int)
            have = 0
            need = int(size / k)
            
            furthestRightFail = -1
            
            # build init window
            initFailed = False
            for i in range(size):
                char = word[i]
                counts[char] += 1
                if i > 0 and not checkTwo(word[i], word[i - 1]):
                    initFailed = True
                    furthestRightFail = i
                if counts[char] == k:
                    have += 1
                elif counts[char] == k + 1:
                    have -= 1
            # we have initial counts
            if not initFailed and have == need:
                resForThis += 1 # init window
            
            l = 0
            r = size # start one shifted off
            
            
            while r < len(word):
                newChar = word[r]
                counts[newChar] += 1
                if counts[newChar] == k:
                    have += 1
                elif counts[newChar] == k + 1:
                    have -= 1
                lostChar = word[l]
                counts[lostChar] -= 1
                if counts[lostChar] == k:
                    have += 1
                elif counts[lostChar] == k - 1:
                    have -= 1
                
                if not checkTwo(word[r], word[r - 1]):
                    furthestRightFail = r
                    
                l += 1
                
                if furthestRightFail <= l and have == need:
                    resForThis += 1
                
                r += 1
                
            
            return resForThis
        
        
        for size in windowSizes:
            res += addToResWithSize(size)
        return res
        
        
                
                
                
                
            
            