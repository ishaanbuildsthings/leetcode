class Solution:
    def minStickers(self, stickers: List[str], target: str) -> int:
        allLetters = sorted(set(target))
        req = Counter(target)

        @cache
        def dp(i, serializedHave):
            deserialized = json.loads(serializedHave)
            if all(deserialized[key] == req[key] for key in deserialized):
                return 0
            if i == len(stickers):
                return inf
            
            

            c = Counter(stickers[i])
            for key in c:
                if key in req:
                    deserialized[key] += c[key]
                    deserialized[key] = min(deserialized[key], req[key])
            ifTakeAndMove = 1 + dp(i + 1, json.dumps(deserialized))
            ifSkip = dp(i + 1, serializedHave)
            # we can take and stay if there are more letters we would need from here
            s = set(stickers[i])
            moreLettersNeededFromHere = False
            for key in req:
                if key in s and deserialized[key] < req[key]:
                    takeAndStay = 1 + dp(i, json.dumps(deserialized))
                    return min(ifSkip, ifTakeAndMove, takeAndStay)
            return min(ifSkip, ifTakeAndMove)
        
        start = {
            key : 0 for key in allLetters
        }
        ans = dp(0, json.dumps(start))
        return ans if ans != inf else -1