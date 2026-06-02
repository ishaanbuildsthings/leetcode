class Solution:
    def toGoatLatin(self, sentence: str) -> str:
            return ' '.join((
                word if word[0].lower() in 'aeiou' else word[1:] + word[0]) + 'ma' + ('a' * (i + 1)) for i, word in enumerate(sentence.split()))