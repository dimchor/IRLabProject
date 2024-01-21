from index import InvertedIndex
from nltk.text import Text
from textprocessing import TextProcessing

class OkapiBM25:
    @staticmethod
    def __tf_tq(word: str, words: list[str]) -> float:
        return words.count(word) / len(words)

    @staticmethod
    def __bm25(index: InvertedIndex, document: Text, words: list[str]) -> float:
        K1 = 1.2
        K3 = 1.2
        B = .75

        rsv = 0.
        for word in words:
            idf = index.idf(word)
            tf_td = index.tf(word, document)
            tf_qt = OkapiBM25.__tf_tq(word, words)

            numerator = ((K1 + 1) * tf_td) * ((K3 + 1) * tf_qt)
            denominator = (K1 * ((1 - B) + B * (len(document) * \
                index.average_length())) + tf_td) * (K3 + tf_qt)
            
            rsv += idf * numerator / denominator

        return rsv

    @staticmethod
    def search(d_index: InvertedIndex, query: str, process_token) -> set:
        words = TextProcessing.process(query, process_token)

        ranks = []
        for i in range(len(d_index)):
            score = OkapiBM25.__bm25(d_index, d_index[i], words)
            if score == 0.:
                continue
            ranks.append((i, score))

        ranks.sort(key=lambda item: item[1], reverse=True)

        return set([d for d, _ in ranks])