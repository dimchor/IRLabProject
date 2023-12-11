import webcrawler
from textprocessing import TextProcessing
import time

def get_sample_data():
    try:
        publications = webcrawler.PubMed.crawl('covid')
        webcrawler.Publication.export_publications(
            f'/data/data-{int(time.time())}.json', publications)
    except webcrawler.InvalidRequestException as e:
        print(e)


def main():
    
    # TODO: add proper input handling from a web server (flask)

    # get_sample_data()

    # process data

    # TODO: improve JSON parsing 
    publications = webcrawler.Publication.import_publications(
        '/data/data-1702228931.json')
    
    TextProcessing.download_dependencies()
    for publication in publications:
        processed_abstract = []
        tokens = TextProcessing.tokenize(publication.abstract.lower())
        for token in tokens:
            if TextProcessing.is_special(token) or \
                TextProcessing.is_stopword(token):
                continue
            processed_abstract.append(TextProcessing.stem(token))

        print(processed_abstract)

    pass


if __name__ == "__main__":
    main()

