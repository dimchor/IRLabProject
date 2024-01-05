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
