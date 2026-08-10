class Solution:
    def strongPasswordChecker(self, password: str) -> int:
        
        hasLower = False
        hasUpper = False
        hasDigit = False

        for v in password:
            if v.isalpha() and v == v.lower():
                hasLower = True
            if v.isalpha() and v == v.upper():
                hasUpper = True
            if v.isdigit():
                hasDigit = True

        runs = []
        currV = password[0]
        streak = 1
        for i in range(1, len(password)):
            v = password[i]
            if v == currV:
                streak += 1
            else:
                runs.append(streak)
                currV = v
                streak = 1
        runs.append(streak)

        inserts = (int(hasLower) ^ 1) + (int(hasUpper) ^ 1) + (int(hasDigit) ^ 1)
        
        # we trim down
        if len(password) > 20:
            reqDelete = len(password) - 20 # we have to delete down to this length
            # after this, we might still have runs, we will just replace things as needed inside those runs, thats better for breaking up runs rather than deleting

            # but we want to figure out which things to delete first, for instance a delete on a run of size 6 is well-placed, since then only a single replacement can break up the run of size 5

            runMod3ToList = [[], [], []] # maps a run % 3 -> [fullSize, ...] we need fullSize for if we delete on a run of exactly size 3, we don't add it back to the mod3 list since now it is size 2

            for run in runs:
                if run < 3:
                    continue
                runMod3ToList[run % 3].append(run)
            
            for _ in range(reqDelete):
                if runMod3ToList[0]:
                    popped = runMod3ToList[0].pop()
                    if popped > 3:
                        runMod3ToList[2].append(popped - 1)
                elif runMod3ToList[1]:
                    popped = runMod3ToList[1].pop()
                    runMod3ToList[0].append(popped - 1)
                elif runMod3ToList[2]:
                    popped = runMod3ToList[2].pop()
                    runMod3ToList[1].append(popped - 1)
            
            replacements = 0
            
            for lst in runMod3ToList:
                for runSz in lst:
                    replacements += runSz // 3
            
            trueReplacements = max(inserts, replacements)

            return reqDelete + trueReplacements


        
        if len(password) < 6:
            # at most one run >= 3, we can break it up
            return max(6 - len(password), inserts)
        

        # for every run, find how many replacements we need
        # 3 4 5 -> 1
        # 6 7 8 -> 2
        # 9 10 11 -> 3

        replaces = 0
        for run in runs:
            replaces += run // 3

        replaces = max(replaces, inserts)

        return replaces
        



