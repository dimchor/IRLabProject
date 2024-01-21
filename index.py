from nltk.text import TextCollection, Text
from webcrawler import Publication

class InvertedIndex(TextCollection):
    def __init__(self, publications: list[list[str]]):
        text_publications = []
        for publication in publications:
            text_publications.append(Text(publication))
        super().__init__(text_publications)

    def __len__(self):
        return len(self._texts)

    def __getitem__(self, index) -> Text:
        return self._texts[index]
    
    def contains(self, input: str) -> set[int]:
        s = set()
        for i in range(len(self)):
            if input in self._texts[i].tokens:
                s.add(i)
        return s
    
    def not_contains(self, input: str) -> set[int]:
        s = set()
        for i in range(len(self)):
            if input not in self._texts[i].tokens:
                s.add(i)
        return s

    def average_length(self) -> float:
        sum = 0
        for text in self._texts:
            sum += len(text)
        return sum / len(self._texts)
