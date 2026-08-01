class Solution:
    def canFormArray(self, arr: List[int], pieces: List[List[int]]) -> bool:
        i = 0
        numToPiecesI = {
            p[0] : i for i, p in enumerate(pieces)
        }
        while i < len(arr):
            target = arr[i]
            if target not in numToPiecesI:
                return False
            piece = pieces[numToPiecesI[target]]
            if piece == arr[i:i+len(piece)]:
                i += len(piece)
            else:
                return False
        
        return True