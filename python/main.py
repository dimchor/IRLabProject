import webcrawler
from textprocessing import TextProcessing
from index import InvertedIndex
import boolean
import time

# temporary functions

def get_sample_data():
    try:
        publications = webcrawler.PubMed.crawl('covid')
        webcrawler.Publication.export_publications(
            f'/data/data-{int(time.time())}.json', publications)
    except webcrawler.InvalidRequestException as e:
        print(e)

def process_publications(
        publications: list[webcrawler.Publication]) -> list[list[str]]:
    processed_publications = []
    for publication in publications:
        processed_publication = []
        tokens = TextProcessing.tokenize(str(publication).lower())
        for token in tokens:
            if TextProcessing.is_special(token) or \
                TextProcessing.is_stopword(token):
                continue
            processed_publication.append(TextProcessing.stem(token))
        processed_publications.append(processed_publication)
    return processed_publications

def print_tokens(tokens: list[boolean.Token]) -> None:
    for token in tokens:
        print(token.value, end='')
    print("")

def main():
    
    # TODO: add proper input handling from a web server (flask)

    # get_sample_data()

    # process data

    # TODO: improve JSON parsing 

    
    publications = webcrawler.Publication.import_publications(
        '../data/data-1704454765.json')

    TextProcessing.download_dependencies()

    processed_publications = process_publications(publications)

    inverted_index = InvertedIndex(processed_publications)

    #print(inverted_index.contains('heart'))
    #print(inverted_index.idf('covid'))
    

    lexer = boolean.Lexer('"covid-19" & ! ("heart" | "covid")')

    tokens = None
    try:
        tokens = lexer.tokenize()
        boolean.check_syntax(tokens)
        #print_tokens(tokens)
        print("")
        dm = boolean.DeMorgan(tokens)
        tokens = dm.convert()
        #print_tokens(tokens)

        tokens = boolean.convert_to_sets(tokens, inverted_index)
        eval = boolean.Evaluate(tokens)
        results = eval.evaluate_infix()

        print(results)
    except Exception as e:
        print(e)

    pass


if __name__ == "__main__":
    main()

