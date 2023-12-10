import webcrawler
import json
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

    publications = webcrawler.Publication.import_publications(
        '/data/data-1702228931.json')
    
    for publication in publications:
        print(publication)

    pass


if __name__ == "__main__":
    main()

