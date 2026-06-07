MORSE = [".-","-...","-.-.","-..",".","..-.","--.","....","..",".---","-.-",".-..","--","-.","---",".--.","--.-",".-.","...","-","..-","...-",".--","-..-","-.--","--.."]

class Solution:
    def uniqueMorseRepresentations(self, words: List[str]) -> int:
        allMorses = set()
        for w in words:
            morseArr = []
            for c in w:
                index = ord(c) - ord('a')
                morseArr.append(MORSE[index])
            allMorses.add(''.join(morseArr))
        return len(allMorses)