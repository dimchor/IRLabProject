from index import InvertedIndex
from textprocessing import TextProcessing
import math
from functools import reduce 

class VectorSpaceModel:
    @staticmethod
    def __norm(vector: list[float]) -> float:
        sum = 0.
        for item in vector:
            sum += item ** 2
        return math.sqrt(sum)

    @staticmethod
    def __normalize(vector: list[float]) -> list[float]:
        norm  = VectorSpaceModel.__norm(vector)
        assert norm > 0, "Norm must be non-zero."
        for item in vector:
            item /= norm
        return vector

    @staticmethod
    def __tf_idf_list(index: InvertedIndex, words: list[str]) \
        -> list[list[float]]:

        tf_idf_index = []
        for i in range(len(index)):
            tf_idf_words = []
            for word in words:
                tf_idf_words.append(index.tf_idf(word, index[i]))
            tf_idf_index.append(tf_idf_words)
        return tf_idf_index

    @staticmethod
    def search(d_index: InvertedIndex, query: str, process_token):
        processed_tokens = TextProcessing.process(query, process_token)

        d_tf_idf_l = VectorSpaceModel.__tf_idf_list(d_index, processed_tokens)

        ranks = []
        index = 0
        for document in d_tf_idf_l:
            try:
                ranks.append((index, reduce(lambda a, b: a + b, VectorSpaceModel.__normalize(document))))
            except:
                pass
            index += 1

        ranks.sort(key=lambda item: item[1], reverse=True)

        return set([d for d, _ in ranks])