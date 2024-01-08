import nltk
from webcrawler import Publication

class InvertedIndex:
    def __init__(self, publications: list[list[str]]):
        self.__publications = []
        for publication in publications:
            self.__publications.append(nltk.text.Text(publication))

    def __len__(self):
        return len(self.__publications)

    def __getitem__(self, index) -> nltk.text.Text:
        return self.__publications[index]
    
    def count(self, input: str) -> dict[int, int]:
        freq = {}
        for i in range(len(self.__publications)):
            c = self.__publications[i].count(input)
            if c < 1:
                continue
            freq[i] = c
        return freq
